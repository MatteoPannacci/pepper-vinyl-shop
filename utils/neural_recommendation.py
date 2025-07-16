import os
import numpy as np
import pandas as pd
import networkx as nx
import tensorflow as tf
import pickle


UTILS_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_DIR = os.path.dirname(UTILS_DIR)
DATASET_DIR = os.path.join(MAIN_DIR, "data")
MODELS_DIR = os.path.join(MAIN_DIR, "models")



def build_graph(seed=42):
    df = pd.read_csv(os.path.join(DATASET_DIR, "buys.csv"))
    users = df['client'].unique().tolist()
    items = df['vinyl'].unique().tolist()

    user2id = {u: i for i, u in enumerate(users)}
    item2id = {v: i + len(users) for i, v in enumerate(items)}
    id2user = {i: u for u, i in user2id.items()}
    id2item = {i: v for v, i in item2id.items()}

    # Count how many times each vinyl appears
    vinyl_counts = df['vinyl'].value_counts()

    train_edges = []
    val_edges = []

    rng = np.random.RandomState(seed)

    for user in users:
        user_df = df[df['client'] == user]
        user_edges = list(user_df.itertuples(index=False))

        if len(user_edges) == 0:
            continue

        # Separate edges where vinyl occurs only once globally
        single_occurrence_edges = [e for e in user_edges if vinyl_counts[e.vinyl] == 1]
        other_edges = [e for e in user_edges if vinyl_counts[e.vinyl] > 1]

        # Always add single-occurrence vinyl edges to train set
        train_edges.extend(single_occurrence_edges)

        # Shuffle other edges and add all but one to train, one to val if possible
        rng.shuffle(other_edges)
        if len(other_edges) > 1:
            train_edges.extend(other_edges[1:])
            val_edges.append(other_edges[0])
        else:
            # If no edges or only one, just add to train
            train_edges.extend(other_edges)

    G = nx.Graph()
    for row in train_edges:
        G.add_edge(user2id[row.client], item2id[row.vinyl])

    val_pairs = [(user2id[row.client], item2id[row.vinyl]) for row in val_edges]

    return G, user2id, item2id, id2user, id2item, len(users), len(items), train_edges, val_pairs


def normalize_adj(adj):
    rowsum = np.array(adj.sum(1))
    d_inv_sqrt = np.power(rowsum, -0.5).flatten()
    d_inv_sqrt[np.isinf(d_inv_sqrt)] = 0.
    d_mat_inv_sqrt = np.diag(d_inv_sqrt)
    return d_mat_inv_sqrt.dot(adj).dot(d_mat_inv_sqrt)


def train_model(hidden_dim=32, epochs=100, lr=0.01, num_samples=1024, top_k=1, n_layers=3):
    # Build graph and mappings
    G, user2id, item2id, id2user, id2item, n_users, n_items, train_edges, val_pairs = build_graph()
    N = n_users + n_items
    
    # Precompute normalized adjacency
    A = nx.adjacency_matrix(G).todense()
    A_norm = A

    # TensorFlow placeholders
    tf.reset_default_graph()
    A_ph = tf.placeholder(tf.float32, [N, N], name="A")
    uid_ph = tf.placeholder(tf.int32, [None], name="uids")
    pos_iid_ph = tf.placeholder(tf.int32, [None], name="pos_iids")
    neg_iid_ph = tf.placeholder(tf.int32, [None], name="neg_iids")

    # LightGCN: node embeddings without weights or activations
    E0 = tf.Variable(tf.random_normal([N, hidden_dim], stddev=0.1), name="embeddings_0")
    all_embeddings = [E0]

    # Propagate embeddings through adjacency
    for layer in range(n_layers):
        next_emb = tf.matmul(A_ph, all_embeddings[-1])
        all_embeddings.append(next_emb)

    # Aggregate embeddings (mean of all layers)
    H = E0
    for layer, embeddings in enumerate(all_embeddings[1:]):
        H += embeddings * 1/(layer+1)

    # Gather user/item representations
    user_emb = tf.gather(H, uid_ph)                          # [batch, hidden_dim]
    pos_item_emb = tf.gather(H, pos_iid_ph)                 # [batch, hidden_dim]
    neg_item_emb = tf.gather(H, neg_iid_ph)                 # [batch, hidden_dim]

    # BPR loss
    pos_score = tf.reduce_sum(user_emb * pos_item_emb, axis=1)
    neg_score = tf.reduce_sum(user_emb * neg_item_emb, axis=1)
    loss = -tf.reduce_mean(tf.log(tf.nn.sigmoid(pos_score - neg_score) + 1e-8))

    # Optimizer
    train_step = tf.train.AdamOptimizer(lr).minimize(loss)

    # Load user positive interactions
    df = pd.read_csv(os.path.join(DATASET_DIR, "buys.csv"))

    user_pos = {}
    for _, row in df.iterrows():
        uid = user2id[row['client']]
        iid = item2id[row['vinyl']]
        user_pos.setdefault(uid, set()).add(iid)

    all_items = list(item2id.values())

    # Build seen items for masking
    seen_items = {u: [] for u in user_pos.keys()}
    for u, i, _ in train_edges:
        uid = user2id[u]
        iid = item2id[i]
        seen_items[uid].append(iid)

    # Training
    sess = tf.Session()
    sess.run(tf.global_variables_initializer())

    for epoch in range(epochs):
        uids, pos_iids, neg_iids = [], [], []
        for _ in range(num_samples):
            u = np.random.choice(n_users)
            if u not in user_pos or not user_pos[u]:
                continue
            i = np.random.choice(list(user_pos[u]))
            j = np.random.choice(all_items)
            while j in user_pos[u]:
                j = np.random.choice(all_items)
            uids.append(u)
            pos_iids.append(i)
            neg_iids.append(j)

        feed_dict = {A_ph: A_norm,
                     uid_ph: uids,
                     pos_iid_ph: pos_iids,
                     neg_iid_ph: neg_iids}
        _, l = sess.run([train_step, loss], feed_dict=feed_dict)

        if epoch % 10 == 0:
            # Compute final embeddings for evaluation
            embeddings = sess.run(H, feed_dict={A_ph: A_norm})
            normed_emb = embeddings / (np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-8)

            # Evaluate Top-K accuracy on validation set
            correct = 0
            item_offset = n_users
            for u, pos_i in val_pairs:
                user_vec = normed_emb[u]
                scores = np.dot(normed_emb[item_offset:], user_vec)

                # Mask training items
                for ti in seen_items[u]:
                    scores[ti - item_offset] = -np.inf

                topk = np.argsort(scores)[-top_k:][::-1]
                if (pos_i - item_offset) in topk:
                    correct += 1
            val_acc = float(correct) / len(val_pairs)
            print("Epoch {}: BPR Loss = {:.4f}, Top-{} Val Acc = {:.4f}".format(epoch, l, top_k, val_acc))

    # Save final model
    final_embeddings = sess.run(H, feed_dict={A_ph: A_norm})
    with open(os.path.join(MODELS_DIR, "recommender_model.pkl"), "wb") as f:
        pickle.dump((final_embeddings, user2id, item2id, id2user, id2item), f)

    sess.close()


def give_recommendations(username, top_k=5):
    model_path = os.path.join(MODELS_DIR, "recommender_model.pkl")
    with open(model_path, "rb") as f:
        embeddings, user2id, item2id, id2user, _ = pickle.load(f)

    if username not in user2id:
        raise ValueError("User not found")

    uid = user2id[username]

    # Normalize embeddings
    normed_emb = embeddings / (np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-8)
    user_vec = normed_emb[uid]

    item_indices = np.array(list(item2id.values()))
    item_vecs = normed_emb[item_indices]

    # Vectorized cosine similarity
    cosine_scores = np.dot(item_vecs, user_vec)

    # Map back to item ids
    idx_to_item = {v: k for k, v in item2id.items()}
    scores = [(idx_to_item[idx], score) for idx, score in zip(item_indices, cosine_scores)]

    # Filter out already seen items
    df = pd.read_csv(os.path.join(DATASET_DIR, "buys.csv"))
    seen = set(df[df['client'] == username]['vinyl'])
    ranked = sorted(scores, key=lambda x: -x[1])
    
    recommendations = [i for i, _ in ranked if i not in seen][:top_k]
    return recommendations
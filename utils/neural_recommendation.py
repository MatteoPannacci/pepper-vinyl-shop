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


def build_graph():
    df = pd.read_csv(os.path.join(DATASET_DIR, "buys.csv"))
    users = df['client'].unique().tolist()
    items = df['vinyl'].unique().tolist()

    user2id = dict((u, i) for i, u in enumerate(users))
    item2id = dict((v, i + len(users)) for i, v in enumerate(items))
    id2user = dict((i, u) for u, i in user2id.iteritems())
    id2item = dict((i, v) for v, i in item2id.iteritems())

    G = nx.Graph()
    for _, row in df.iterrows():
        G.add_edge(user2id[row['client']], item2id[row['vinyl']])

    return G, user2id, item2id, id2user, id2item, len(users), len(items)


def normalize_adj(adj):
    rowsum = np.array(adj.sum(1))
    d_inv_sqrt = np.power(rowsum, -0.5).flatten()
    d_inv_sqrt[np.isinf(d_inv_sqrt)] = 0.
    d_mat_inv_sqrt = np.diag(d_inv_sqrt)
    return d_mat_inv_sqrt.dot(adj).dot(d_mat_inv_sqrt)


def train_gcn_bpr_model(hidden_dim=32, epochs=100, lr=0.01, num_samples=1024):
    G, user2id, item2id, id2user, id2item, n_users, n_items = build_graph()
    N = n_users + n_items

    A = nx.adjacency_matrix(G).todense()
    A_norm = normalize_adj(A + np.eye(N))
    X = np.eye(N)  # One-hot features

    tf.reset_default_graph()
    X_ph = tf.placeholder(tf.float32, [N, N])
    A_ph = tf.placeholder(tf.float32, [N, N])
    uid_ph = tf.placeholder(tf.int32, [None])
    pos_iid_ph = tf.placeholder(tf.int32, [None])
    neg_iid_ph = tf.placeholder(tf.int32, [None])

    # GCN layers
    W0 = tf.Variable(tf.random_normal([N, hidden_dim], stddev=0.1))
    W1 = tf.Variable(tf.random_normal([hidden_dim, hidden_dim], stddev=0.1))

    H1 = tf.nn.relu(tf.matmul(A_ph, tf.matmul(X_ph, W0)))
    H = tf.matmul(A_ph, tf.matmul(H1, W1))  # Final embeddings

    user_emb = tf.gather(H, uid_ph)
    pos_item_emb = tf.gather(H, pos_iid_ph)
    neg_item_emb = tf.gather(H, neg_iid_ph)

    # BPR loss
    pos_score = tf.reduce_sum(tf.multiply(user_emb, pos_item_emb), axis=1)
    neg_score = tf.reduce_sum(tf.multiply(user_emb, neg_item_emb), axis=1)
    loss = -tf.reduce_mean(tf.log(tf.nn.sigmoid(pos_score - neg_score)))

    train_step = tf.train.AdamOptimizer(lr).minimize(loss)
    sess = tf.Session()
    sess.run(tf.global_variables_initializer())

    # Training data: positive interactions
    df = pd.read_csv(os.path.join(DATASET_DIR, "buys.csv"))
    user_pos = {}
    for _, row in df.iterrows():
        uid = user2id[row['client']]
        iid = item2id[row['vinyl']]
        user_pos.setdefault(uid, set()).add(iid)

    all_items = list(item2id.values())

    for epoch in range(epochs):
        uids, pos_iids, neg_iids = [], [], []
        for _ in range(num_samples):
            u = np.random.choice(n_users)
            if u not in user_pos or len(user_pos[u]) == 0:
                continue
            i = np.random.choice(list(user_pos[u]))
            j = np.random.choice(all_items)
            while j in user_pos[u]:
                j = np.random.choice(all_items)
            uids.append(u)
            pos_iids.append(i)
            neg_iids.append(j)

        feed = {
            X_ph: X,
            A_ph: A_norm,
            uid_ph: uids,
            pos_iid_ph: pos_iids,
            neg_iid_ph: neg_iids
        }
        _, l = sess.run([train_step, loss], feed_dict=feed)
        if epoch % 10 == 0:
            print("Epoch %d: BPR Loss = %.4f" % (epoch, l))

    final_embeddings = sess.run(H, feed_dict={X_ph: X, A_ph: A_norm})

    with open(os.path.join(MODELS_DIR, "gcn_model_bpr.pkl"), "wb") as f:
        pickle.dump((final_embeddings, user2id, item2id, id2user, id2item), f)

    sess.close()



def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8)


def give_recommendations(username, top_k=5):
    model_path = os.path.join(MODELS_DIR, "gcn_model.pkl")
    with open(model_path, "rb") as f:
        embeddings, user2id, item2id, id2user, id2item = pickle.load(f)

    if username not in user2id:
        raise ValueError("User not found")

    uid = user2id[username]
    user_emb = embeddings[uid]

    scores = []
    for iid, emb_idx in item2id.iteritems():
        score = cosine_similarity(user_emb, embeddings[emb_idx])
        scores.append((iid, score))

    dataset_file = os.path.join(DATASET_DIR, "buys.csv")
    df = pd.read_csv(dataset_file)
    seen = set(df[df['client'] == username]['vinyl'])

    ranked = sorted(scores, key=lambda x: -x[1])
    recommendations = [id2item[i] for i, _ in ranked if id2item[i] not in seen][:top_k]
    return recommendations

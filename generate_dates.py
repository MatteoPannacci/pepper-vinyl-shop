from datetime import datetime, timedelta
import random
import pandas as pd

# Load user data
users_raw = """
username,fav_genre,fav_author,last_visit
luca,jazz,miles davis,2023-05-14
emanuele,hip hop,kendrick lamar,2022-11-03
ali,classical,antonio vivaldi,2024-02-19
matteo,classical,ludwig van beethoven,2020-08-21
anna,progressive rock,pink floyd,2021-12-08
marco,rock,the beatles,2025-06-11
giulia,pop,michael jackson,2022-01-30
federico,hard rock,ac/dc,2023-07-25
valentina,glam rock,david bowie,2020-04-16
riccardo,worldbeat,paul simon,2025-04-03
elisa,pop rock,prince,2021-03-27
andrea,grunge,pearl jam,2024-06-09
francesca,alternative rock,radiohead,2023-10-19
simone,indie rock,the smiths,2020-09-05
martina,pop soul,adele,2025-01-12
davide,r&b,beyonce,2024-12-03
carlo,electronic rock,radiohead,2021-05-28
silvia,thrash metal,metallica,2023-02-17
stefano,punk rock,green day,2022-06-22
paolo,hip hop,kendrick lamar,2016-09-11
giovanni,indie rock,arcade fire,2023-09-02
chiara,art pop,kate bush,2024-11-12
lorenzo,neo soul,jungle,2023-10-30
marta,dream pop,m83,2024-07-05
daniele,grunge,nirvana,2023-03-18
camilla,folk,joni mitchell,2021-06-22
fabio,alternative rock,the cure,2025-05-03
ilaria,art rock,david bowie,2023-12-08
serena,alt r&b,the weeknd,2024-08-27
alessandro,garage rock,arctic monkeys,2022-04-22
giacomo,electronic,daft punk,2025-06-01
rosa,pop soul,adele,2024-01-05
beatrice,electropop,lorde,2023-11-14
martino,folk rock,bob dylan,2022-12-10
teodora,indie pop,the xx,2021-10-06
ludovico,jazz,john coltrane,2024-09-29
nicole,baroque pop,fiona apple,2023-02-15
vittorio,hardcore punk,turnstile,2025-03-27
sara,ambient techno,aphex twin,2024-06-21
nicolas,post-punk revival,interpol,2023-04-11
allegra,trip hop,massive attack,2022-07-07
carla,downtempo,bonobo,2024-05-16
gabriele,lo-fi indie,neutral milk hotel,2023-01-30
letizia,experimental hip hop,death grips,2022-10-09
michele,alternative hip hop,gorillaz,2024-03-14
nadia,art rock,radiohead,2025-02-26
tommaso,psychedelic rock,love,2024-07-04
noemi,experimental,bjork,2023-06-12
enrico,emo,sunny day real estate,2024-09-08
"""

# Convert user data to DataFrame
users_df = pd.read_csv(pd.compat.StringIO(users_raw))
users_df['last_visit'] = pd.to_datetime(users_df['last_visit'])


buys_raw = """
client,vinyl
luca,abbey road
luca,parachutes
luca,purple rain
luca,let it bleed
luca,the rise and fall of ziggy stardust
luca,master of puppets
luca,kind of blue
luca,dark side of the moon
luca,a love supreme
luca,21
luca,ten
luca,disintegration
luca,blue
luca,good kid maad city
emanuele,damn
emanuele,hotel california
emanuele,the chronic
emanuele,illmatic
emanuele,to pimp a butterfly
emanuele,let it bleed
emanuele,thriller
emanuele,a moon shaped pool
emanuele,good kid maad city
ali,the four seasons
ali,hotel california
ali,abbey road
ali,the chronic
ali,21
ali,illmatic
ali,kind of blue
ali,symphony no 5
ali,nevermind
ali,graceland
ali,blue
ali,a love supreme
matteo,the four seasons
matteo,abbey road
matteo,bad
matteo,american idiot
matteo,back in black
matteo,illmatic
matteo,to pimp a butterfly
matteo,the queen is dead
matteo,dark side of the moon
matteo,symphony no 5
matteo,ten
matteo,disintegration
matteo,kind of blue
matteo,blue
anna,damn
anna,abbey road
anna,bad
anna,symphony no 5
anna,born to run
anna,the wall
anna,rumours
anna,dark side of the moon
anna,21
anna,ok computer
anna,graceland
anna,ten
anna,disintegration
anna,blue
marco,hotel california
marco,abbey road
marco,the four seasons
marco,american idiot
marco,born to run
marco,to pimp a butterfly
marco,let it bleed
marco,master of puppets
marco,the queen is dead
marco,rumours
marco,disintegration
marco,blue
giulia,bad
giulia,parachutes
giulia,kid a
giulia,thriller
giulia,lemonade
giulia,dark side of the moon
giulia,21
giulia,nevermind
giulia,ok computer
giulia,ten
giulia,ctrl
giulia,a moon shaped pool
giulia,disintegration
federico,abbey road
federico,the chronic
federico,parachutes
federico,back in black
federico,a love supreme
federico,purple rain
federico,to pimp a butterfly
federico,let it bleed
federico,thriller
federico,lemonade
federico,dark side of the moon
federico,ten
federico,master of puppets
federico,disintegration
valentina,american idiot
valentina,a love supreme
valentina,born to run
valentina,back in black
valentina,the rise and fall of ziggy stardust
valentina,rumours
valentina,dark side of the moon
valentina,nevermind
valentina,graceland
valentina,ten
valentina,blue
valentina,disintegration
riccardo,parachutes
riccardo,american idiot
riccardo,illmatic
riccardo,to pimp a butterfly
riccardo,let it bleed
riccardo,master of puppets
riccardo,a love supreme
riccardo,graceland
riccardo,disintegration
riccardo,blue
elisa,bad
elisa,parachutes
elisa,american idiot
elisa,illmatic
elisa,kid a
elisa,purple rain
elisa,let it bleed
elisa,the wall
elisa,lemonade
elisa,dark side of the moon
elisa,ok computer
elisa,ten
elisa,disintegration
elisa,blue
andrea,abbey road
andrea,bad
andrea,parachutes
andrea,to pimp a butterfly
andrea,let it bleed
andrea,nevermind
andrea,ok computer
andrea,ten
andrea,disintegration
andrea,blue
francesca,the four seasons
francesca,21
francesca,parachutes
francesca,american idiot
francesca,illmatic
francesca,kid a
francesca,kind of blue
francesca,symphony no 5
francesca,nevermind
francesca,ok computer
francesca,blue
francesca,disintegration
simone,damn
simone,american idiot
simone,back in black
simone,kid a
simone,the queen is dead
simone,master of puppets
simone,the wall
simone,rumours
simone,21
simone,disintegration
simone,blue
martina,the four seasons
martina,damn
martina,illmatic
martina,kid a
martina,purple rain
martina,the rise and fall of ziggy stardust
martina,the queen is dead
martina,master of puppets
martina,a love supreme
martina,21
martina,graceland
martina,ten
martina,disintegration
martina,blue
davide,the four seasons
davide,damn
davide,illmatic
davide,the rise and fall of ziggy stardust
davide,lemonade
davide,symphony no 5
davide,ok computer
davide,ten
davide,disintegration
davide,blue
carlo,back in black
carlo,born to run
carlo,kid a
carlo,purple rain
carlo,the queen is dead
carlo,the wall
carlo,the rise and fall of ziggy stardust
carlo,dark side of the moon
carlo,disintegration
carlo,blue
silvia,the four seasons
silvia,back in black
silvia,born to run
silvia,kid a
silvia,to pimp a butterfly
silvia,master of puppets
silvia,the rise and fall of ziggy stardust
silvia,symphony no 5
silvia,nevermind
silvia,ok computer
silvia,graceland
silvia,disintegration
silvia,blue
stefano,american idiot
stefano,illmatic
stefano,kid a
stefano,to pimp a butterfly
stefano,lemonade
stefano,nevermind
stefano,ok computer
stefano,graceland
stefano,ten
stefano,disintegration
stefano,blue
paolo,damn
paolo,hotel california
paolo,bad
paolo,the chronic
paolo,born to run
paolo,illmatic
paolo,to pimp a butterfly
paolo,let it bleed
paolo,master of puppets
paolo,thriller
paolo,kind of blue
paolo,lemonade
paolo,disintegration
paolo,blue
giovanni,funeral
giovanni,hot fuss
giovanni,turn on the bright lights
giovanni,in the aeroplane over the sea
giovanni,xx
giovanni,blue
giovanni,disintegration
chiara,hounds of love
chiara,homogenic
chiara,no shape
chiara,blackstar
chiara,disintegration
chiara,lemonade
lorenzo,lp
lorenzo,black sands
lorenzo,innerworld
lorenzo,emotion
lorenzo,xx
lorenzo,trilogy
marta,saturdays = youth
marta,demon days
marta,midnight marauders
marta,xx
marta,hot fuss
daniele,nevermind
daniele,ten
daniele,disintegration
daniele,doolittle
daniele,grace
camilla,blue
camilla,highway 61 revisited
camilla,whats going on
camilla,aint that good news
camilla,kind of blue
camilla,bitches brew
camilla,a love supreme
fabio,disintegration
fabio,doolittle
fabio,the four seasons
fabio,symphony no 5
fabio,homogenic
fabio,vespertine
ilaria,blackstar
ilaria,the rise and fall of ziggy stardust
ilaria,let it bleed
ilaria,grace
serena,house of balloons
serena,trilogy
serena,after hours
serena,channel orange
serena,ctrl
alessandro,am
alessandro,hot fuss
alessandro,xx
alessandro,turn on the bright lights
alessandro,funeral
alessandro,blue
alessandro,elephant
giacomo,random access memories
giacomo,disintegration
giacomo,demon days
giacomo,melodrama
giacomo,currents
giacomo,in rainbows
rosa,21
rosa,good kid maad city
rosa,emotion
rosa,lemonade
rosa,xx
rosa,blackstar
beatrice,melodrama
beatrice,xx
beatrice,emotion
beatrice,random access memories
beatrice,blackstar
martino,highway 61 revisited
martino,whats going on
martino,aint that good news
martino,blue
martino,bitches brew
martino,a love supreme
teodora,xx
teodora,diary
teodora,emotion
teodora,hot fuss
teodora,in the aeroplane over the sea
ludovico,a love supreme
ludovico,kind of blue
ludovico,bitches brew
ludovico,midnight marauders
ludovico,mezzanine
ludovico,master of puppets
nicole,tidal
nicole,blackstar
nicole,homogenic
nicole,vespertine
nicole,ctrl
vittorio,time & space
vittorio,american idiot
vittorio,the chronic
vittorio,master of puppets
vittorio,disintegration
vittorio,good kid maad city
sara,selected ambient works 85-92
sara,innerworld
sara,vespertine
sara,saturdays = youth
sara,black sands
nicolas,turn on the bright lights
nicolas,funeral
nicolas,in the aeroplane over the sea
nicolas,hot fuss
nicolas,xx
allegra,mezzanine
allegra,entroducing
allegra,black sands
allegra,disintegration
allegra,a moon shaped pool
carla,black sands
carla,innerworld
carla,saturdays = youth
carla,demon days
carla,xx
carla,emotion
gabriele,in the aeroplane over the sea
gabriele,funeral
gabriele,xx
gabriele,hot fuss
gabriele,blue
letizia,the money store
letizia,melodrama
letizia,demon days
letizia,ctrl
letizia,emotion
michele,demon days
michele,melodrama
michele,random access memories
michele,channel orange
michele,ctrl
nadia,in rainbows
nadia,kid a
nadia,ok computer
nadia,a moon shaped pool
nadia,blackstar
tommaso,forever changes
tommaso,soulfly
tommaso,homogenic
tommaso,highway 61 revisited
noemi,vespertine
noemi,homogenic
noemi,blackstar
noemi,disintegration
noemi,a moon shaped pool
enrico,diary
enrico,disintegration
enrico,demon days
enrico,mezzanine
"""


buys_df = pd.read_csv(pd.compat.StringIO(buys_raw))

# Generate a realistic purchase date based on last_visit
def random_date_near(visit_date, days_range=500):
    offset = random.randint(-days_range, 0)
    return visit_date + timedelta(days=offset)

# Map user last visit to purchases
user_last_visit = dict(zip(users_df["username"], users_df["last_visit"]))
buys_df["date"] = buys_df["client"].map(user_last_visit).apply(lambda d: random_date_near(d))

buys_df.to_csv("new_buys.csv", index=False)

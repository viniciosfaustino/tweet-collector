from tweetCollector import *
_track = ['covid19', 'coronavirus', 'covid-19']
collector = TweetCollector('covid19', track=_track)
collector.start_stream()
collector.save_tweets_to_file()

# get_text_from_status()

_track = ["quero morrer", "vou me matar", "suicidio", "cortei meu pulso", "não quero mais viver",
          "n quero mais viver", "prefiro morrer", "vou me suicidar", "vou acabar com a minha vida", "desisti de viver",
          "tentei me matar", "tentei suicidio", "vou acabar com a minha vida", "minha carta de suicidio",
          "nunca mais acordar", "não consigo continuar", 'não vale a pena viver', 'não vale mais a pena viver',
          'n vale mais a pena viver', 'n vale a pena viver', 'melhor sem mim', 'melhor estar morto',
          'devia estar morto', 'plano de suicidio', 'pacto de suicidio', 'cansado de viver', 'cansado da minha vida',
          'não quero estar aqui', 'n queria estar vivo', 'não queria estar vivo', 'vou dormir pra sempre',
          'vou me suicidar', 'cometer suicido', 'só queria que acabasse', 'tirar minha vida', 'pensamentos depressivos',
          'estou deprimido', 'to deprimido', 'eu queria estar morto']
#collector = TweetCollector("ideacao", track=_track, max_tweets=5000)
#_track = ['GreveDosCaminhoneiros']
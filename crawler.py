import os
from os.path import join, dirname
from time import ctime
import json
import tweepy
from dotenv import load_dotenv
from tweetListener import TweetListener, get_text_from_status

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

consumer_key = os.getenv('CONSUMER_KEY')
consumer_secret = os.getenv('CONSUMER_SECRET')
access_token = os.getenv('ACCESS_TOKEN')
access_token_secret = os.getenv('ACCESS_TOKEN_SECRET')

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)


class TweetCollector:
    def __init__(self, name: str, path: str = 'data', max_tweets: int = 100000, timeout: int = 36000, track: list = None):
        self.name = name
        self.tweet_count = 0
        self.path = path
        self.listener = TweetListener(timeout, max_tweets)
        self.stream = tweepy.Stream(auth=api.auth, listener=self.listener)
        self.track = track

    def save_tweets_to_file(self, id_only: bool = False):
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        path = os.path.join(self.path, self.name)
        try:
            os.mkdir(path)
        except Exception:
            pass
        created_at = ctime()
        created_at = created_at.replace(' ', '-')
        if id_only:
            data = {'name': self.name, 'created_at': created_at, "id_str": self.listener.tweets['id_str']}
        else:
            data = {'name': self.name, 'created_at': created_at, "id_str": self.listener.tweets['id_str'],
                    'text': self.listener.tweets['text']}
        filename = self.name+"-"+str(created_at)+'.json'
        file = os.path.join(path, filename)

        with open(file, "w") as f:
            json.dump(data, f, indent=4)

    def start_stream(self, **kwargs):
        try:
            self.stream.filter(track=self.track, languages=['pt', 'en'])

        except Exception as e:
            self.stream.disconnect()
            self.start_stream(**kwargs)


def get_text_from_tweet_id(id_str):
    print(type(id_str))
    try:
        status = api.get_status(id_str, tweet_mode="extended")
        text = get_text_from_status(status)
        text = text.replace("\n", " ")
        return text

    except Exception as e:
        print("Error:", e['message'])
        raise Exception


def retrieve_text_from_json(filepath: str):
    print("retrieve started")
    with open(filepath, 'rb') as f:
        print("json opened")
        file = json.load(f)
        ids = file['id_str']
        text = []
        total = len(ids)
        cont = 1
        print(ids)
        for id_str in ids:
            try:
                tweet_str = get_text_from_tweet_id(id_str)
                text.append(tweet_str)
                print(cont, "of", total, "tweets retrieved")
                cont += 1

            except Exception as e:
                print("Couldn't retrieve tweet", e)
                pass

    txt_filename = os.path.splitext(filepath)[0]+".txt"
    with open(txt_filename, "w") as f:
        for line in text:
            f.write(line+"\n")

# _track = ['quero morrer', "vou me matar", "suicidio", "cortei meu pulso", "não quero mais viver", "n quero mais viver", "prefiro morrer", "vou me suicidar", "vou acabar com a minha vida", "desisti de viver", "tentei me matar", "tentei suicidio", "vou acabar com a minha vida"]
# collector = TweetCollector("ideacao", track=_track)
# _track = ['GreveDosCaminhoneiros']
_track = ['covid19', 'coronavirus', 'covid-19']
collector = TweetCollector('covid19', track=_track)
collector.start_stream()
collector.save_tweets_to_file()
# retrieve_text_from_json("data/ideacao/ideacao-Sun-Feb-16-17:48:49-2020.json")

# retrieve_text_from_json("coronavirus/coronavirus-Thu-Jan-30-15:23:39-2020.json")

#TODO colocar um contador de tweets coletados ou um progress bar
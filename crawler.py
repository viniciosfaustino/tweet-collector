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
    def __init__(self, name: str, path: str = 'data', max_tweets: int = 10000, timeout: int = 36000, track: list = None):
        self.name = name
        self.tweet_count = 0
        self.path = path
        self.listener = TweetListener(timeout, max_tweets)
        self.stream = tweepy.Stream(auth=api.auth, listener=self.listener)
        self.track = track

    def save_tweets_to_file(self, id_only: bool = False):
        if os.path.exists(self.path):
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
            self.stream.filter(track=self.track)

        except Exception as e:
            self.stream.disconnect()
            self.start_stream(**kwargs)


def get_text_from_tweet_id(id_str):
    try:
        status = api.get_status(id_str, tweet_mode="extended")
        text = get_text_from_status(status)
        text = text.replace("\n", " ")
        return text

    except:
        raise Exception


def retrieve_text_from_json(filepath: str):
    with open(filepath, 'r') as f:
        file = json.load(f)
        ids = file['id_str']
        text = []
        total = len(ids)
        cont = 1
        for id_str in ids:
            try:
                tweet_str = get_text_from_tweet_id(id_str)
                text.append(tweet_str)
                print(cont, "of", total, "tweets retrieved")
                cont += 1

            except Exception:
                pass

    txt_filename = os.path.splitext(filepath)[0]+".txt"
    with open(txt_filename, "w") as f:
        for line in text:
            f.write(line+"\n")


collector = TweetCollector("coronavirus", track=['coronavirus', 'corona virus', 'coronavírus', 'corona vírus', 'Wuhan',
                                                 '#nCoV2019', 'ncov2019', '2019ncov'])
collector.start_stream()
collector.save_tweets_to_file()

# retrieve_text_from_json("coronavirus/coronavirus-Thu-Jan-30-15:23:39-2020.json")
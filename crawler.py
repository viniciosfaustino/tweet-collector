import os
from os.path import join, dirname
from time import ctime
import json
import tweepy
from dotenv import load_dotenv
from tweetListener import TweetListener

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
    def __init__(self, name: str, save_tweets: bool = False, path: str = '.', max_tweets: int = 2,
                 timeout: int = 50000, track: list = None):
        self.name = name
        self.tweet_count = 0
        self.save_tweets = save_tweets
        self.path = path
        self.listener = TweetListener(timeout, max_tweets)
        self.stream = tweepy.Stream(auth=api.auth, listener=self.listener)
        self.track = track

    def save_tweets_to_file(self):
        if os.path.exists(self.path):
            path = os.path.join(self.path, self.name)
            try:
                os.mkdir(path)
            except Exception:
                pass
            created_at = ctime()
            created_at = created_at.replace(' ', '-')
            data = {'name': self.name, "id_str": self.listener.tweets, 'created_at': created_at}
            filename = self.name+"-"+str(created_at)+'.json'
            file = os.path.join(path, filename)
            print(file)
            with open(file, "w") as f:
                print(dir(f))
                json.dump(data, f, indent=4)
            print(data)

    def start_stream(self, **kwargs):
        print('start stream')
        try:
            print(self.track)
            self.stream.filter(track=self.track)
        except Exception:
            self.stream.disconnect()
            self.start_stream(**kwargs)

        self.tweet_count = len(self.listener.tweets)
        print(self.tweet_count)

        self.save_tweets_to_file()
        # aqui vai ser chamada a funcao que escreve no arquivo


collector = TweetCollector("coletor", track=['odeio'])
collector.start_stream()

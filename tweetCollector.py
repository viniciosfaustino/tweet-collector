import os
from typing import List
from os.path import join, dirname
from time import ctime
import tweepy
from dotenv import load_dotenv
from tweetListener import TweetListener, get_text_from_status
from argparse import ArgumentParser
import logging

LOG_FORMAT = "[%(levelname)s/%(asctime)-15s] %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

# dotenv_path = join(dirname(__file__), '.env')
load_dotenv(".env/keys.env")

consumer_key = os.getenv('CONSUMER_KEY')
consumer_secret = os.getenv('CONSUMER_SECRET')
access_token = os.getenv('ACCESS_TOKEN')
access_token_secret = os.getenv('ACCESS_TOKEN_SECRET')

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

parser = ArgumentParser()
parser.add_argument("--track", required=True, type=str,
                    help="Text file with the things to track."
                    )
parser.add_argument("--name", required=True, type=str,
                    help="Name of the project."
                    )

parser.add_argument("--output_dir", required=True, type=str,
                    help="Output directory."
                    )

parser.add_argument("--max_tweets", type=int, default=100000,
                    help="Maximum number of tweets to collect."
                    )
parser.add_argument("--checkpoint_after", type=int, default=None,
                    help="Create a checkpoint file after collecting a determined number of tweets."
                    )

class TweetCollector:
    def __init__(self, name: str,
                       path: str = 'data',
                       max_tweets: int = 100000,
                       timeout: int = 36000, 
                       track: List[str] = None, 
                       _lang: List[str] = ['pt'],
                       checkpoint_after: int = None):

        self.tweet_count = 0
        self.listener = TweetListener(name, path, timeout, max_tweets, checkpoint_after)
        self.stream = tweepy.Stream(auth=api.auth, listener=self.listener)
        self.track = track
        self.languages = _lang


    def start_stream(self, **kwargs):
        try:
            logging.info("Stream started, tracking: {}, in {}.".format(self.track, self.languages))
            self.stream.filter(track=self.track, languages=self.languages)

        except Exception as e:
            logging.error("Stream restarting after {}.".format(e))
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

#TODO colocar um contador de tweets coletados ou um progress bar
#TODO entrar em um perfil e pegar todos os tweets do perfil e salvar com o id do usuário
#TODO coletar apenas metadados sobre assuntos, aka - numero de tweets a cada intervalo de tempo

#novas datas para o processo seletivo, se liga no post


def get_tracked_entities(path: str):
    with open(path, "r") as f:
        track = f.readlines()
    
    return [entity.strip("\n") for entity in track]


if __name__ == "__main__":
    args = parser.parse_args()
    track = get_tracked_entities(args.track)
    collector = TweetCollector(args.name, args.output_dir,
                               timeout=240000,
                               max_tweets=args.max_tweets, 
                               checkpoint_after=args.checkpoint_after,
                               track=track)
    # print(track)
    collector.start_stream()

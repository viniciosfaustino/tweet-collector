import os
import sys
import json
import logging
import tweepy

from dotenv import load_dotenv
from multiprocessing import Process
from time import time, sleep
from typing import List
from utils import load_args, get_text_from_status, get_tracked_entities, save_tweets_to_file, get_tweets_from_user_id

LOG_FORMAT = "[%(levelname)s/%(asctime)-15s] %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

consumer_key = os.getenv('CONSUMER_KEY')
consumer_secret = os.getenv('CONSUMER_SECRET')
access_token = os.getenv('ACCESS_TOKEN')
access_token_secret = os.getenv('ACCESS_TOKEN_SECRET')

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)


class TweetCollector(tweepy.StreamListener):
    def __init__(self, name: str, path: str, timeout: int, max_tweets: int, checkpoint_after: int = None,
                 track: List[str] = None, _lang: List[str] = ['pt']):
        super(TweetCollector, self).__init__()
        self.checkpoint_after = checkpoint_after
        self._checkpoints = 0
        self.languages = _lang
        self._max_checkpoints = round(max_tweets / checkpoint_after);
        self.max_tweets = max_tweets
        self.name = name
        self.path = path
        self.started_at = time()
        self.stream = tweepy.Stream(auth=api.auth, listener=self)
        self.timeout = timeout
        self.track = track
        self.tweets = {"user_id": [], "id_str": [], 'text': [], 'hashtags': [], 'mentions': [], 'timestamp': []}

    def add_tweet(self, status):
        text = get_text_from_status(status)
        self.tweets["user_id"].append(status.user.id)
        self.tweets['id_str'].append(status.id_str)
        self.tweets['text'].append(text)
        self.tweets['hashtags'].append([hashtag["text"] for hashtag in status.entities["hashtags"]])
        self.tweets["mentions"].append([user["screen_name"] for user in status.entities["user_mentions"]])
        str_time = status.created_at.strftime("%d-%b-%Y-%H:%M:%S.%f")
        self.tweets['timestamp'].append(str_time)

    def _save(self, message: str):
        logging.info(message)
        writing_process = Process(target=save_tweets_to_file,
                                  args=(self.path, self.name, self.tweets, False))
        writing_process.start()

    def on_status(self, status):
        num_tweets = len(self.tweets['id_str'])
        if self.checkpoint_after is not None:
            if num_tweets > self.max_tweets:
                self._save("Saving file.")
                return False
            if num_tweets > self.checkpoint_after:
                self._checkpoints += 1
                self._save("Creating checkpoint.")
                self.tweets = {"user_id": [], "id_str": [], 'text': [], 'hashtags': [], 'mentions': [], 'timestamp': []}

        elif self._max_checkpoints > self._checkpoints:
            self._save("Saving file.")

        if time() - self.started_at < self.timeout and self._max_checkpoints > self._checkpoints:
            self.add_tweet(status)
        else:
            return False

    def on_error(self, status_code):
        print(sys.stderr, 'Encountered error with status code:', status_code)
        if status_code == 420:
            print("Waiting 2s to restart stream")
            sleep(2)
        print("Stream restarted")
        return True  # Don't kill the stream

    def start_stream(self, **kwargs):
        try:
            logging.info("Stream started, tracking: {}, in {}.".format(self.track, self.languages))
            self.stream.filter(track=self.track, languages=self.languages)

        except Exception as e:
            logging.error("Stream restarting after {}.".format(e))
            self.stream.disconnect()
            self.start_stream(**kwargs)


if __name__ == "__main__":
    args = load_args()
    track = get_tracked_entities(args.track)

    if args.user:
        user = get_tracked_entities(args.user)
        print(user)
        tweets = get_tweets_from_user_id(user[0], api)
        if tweets:
            logging.info("Couldn't get tweets from user {}".format(user[0]))
        save_tweets_to_file(args.output_dir, user, tweets)
    else:
        collector = TweetCollector(args.name, args.output_dir,
                                   timeout=240000,
                                   max_tweets=args.max_tweets,
                                   checkpoint_after=args.checkpoint_after,
                                   track=track)
        # print(track)
        collector.start_stream()

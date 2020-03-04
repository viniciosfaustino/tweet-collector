import sys
from time import time, sleep
from time import ctime
import multiprocessing
import tweepy
import sys
from multiprocessing import Process
import json
import os
from typing import List
import logging

LOG_FORMAT = "[%(levelname)s/%(asctime)-15s] %(message)s"


def save_tweets_to_file(path: str, name: str, tweets: List[str], id_only: bool = False):
    logging.info("Saving {} tweets to {}{}.".format(len(tweets["id_str"]), path, name))
    if not os.path.exists(path):
        os.mkdir(path)
    path = os.path.join(path, name)
    try:
        os.mkdir(path)
    except Exception:
        pass
    created_at = ctime()
    created_at = created_at.replace(' ', '-')
    if id_only:
        data = {'name': name, 'created_at': created_at, "id_str": tweets['id_str'],
                'hashtags': tweets['hashtags'], "mentions":  tweets['mentions']}
    else:
        data = {'name': name, 'created_at': created_at, "id_str": tweets['id_str'],
                'text': tweets['text'], 'timestamp': tweets['timestamp'],
                'hashtags': tweets['hashtags'], "mentions":  tweets['mentions']}
    filename = name+"-"+str(created_at)+'.json'
    file = os.path.join(path, filename)

    with open(file, "w") as f:
        json.dump(data, f, indent=4)


class TweetListener(tweepy.StreamListener):
    def __init__(self, name: str, path: str, timeout: int, max_tweets: int, checkpoint_after: int = None):
        super(TweetListener, self).__init__()
        self.name = name
        self.path = path
        self.max_tweets = max_tweets
        self.checkpoint_after = checkpoint_after
        self.started_at = time()
        self.timeout = timeout
        self.tweets = {"id_str": [], 'text': [], 'hashtags': [], 'mentions': [], 'timestamp': []}

    def on_status(self, status):
        
        if self.checkpoint_after is not None:
            if len(self.tweets['id_str']) > self.checkpoint_after:
                logging.info("Creating checkpoint.")
                writing_process = Process(target=save_tweets_to_file,
                                  args=(self.path, self.name, self.tweets, False))
                writing_process.start()
                # Processo é criado copiando os parametros do original
                self.tweets = {"id_str": [], 'text': [], 'hashtags': [], 'mentions': [], 'timestamp': []}


        if time() - self.started_at < self.timeout and len(self.tweets['id_str']) < self.max_tweets:
            # print(len(self.tweets['id_str']) + 1)
            text = get_text_from_status(status)
            self.tweets['id_str'].append(status.id_str)
            self.tweets['text'].append(text)
            self.tweets["hashtags"].append([hashtag["text"] for hashtag in status.entities["hashtags"]])
            self.tweets["mentions"].append([user["screen_name"] for user in status.entities["user_mentions"]])
            str_time = status.created_at.strftime("%d-%b-%Y-%H:%M:%S.%f")
            self.tweets['timestamp'].append(str_time)
        else:
            return False

    def on_error(self, status_code):
        print(sys.stderr, 'Encountered error with status code:', status_code)
        if status_code == 420:
            print("Waiting 2s to restart stream")
            sleep(2)
        print("Stream restarted")
        return True  # Don't kill the stream


def get_text_from_status(status):
    if hasattr(status, 'retweeted_status'):
        try:
            text = status.retweeted_status.extended_tweet["full_text"]
        except AttributeError:
            try:
                text = status.retweeted_status.full_text
            except AttributeError:
                text = status.retweeted_status.text
    else:
        try:
            text = status.extended_tweet["full_text"]
        except AttributeError:
            try:
                text = status.full_text
            except AttributeError:
                text = status.text
    return text


def print_status_text(status):
    text = get_text_from_status(status)
    print(text[:15], '\n')

import sys
from time import time, sleep
import tweepy


class TweetListener(tweepy.StreamListener):
    def __init__(self, timeout: int, max_tweets: int):
        super(TweetListener, self).__init__()
        self.max_tweets = max_tweets
        self.started_at = time()
        self.timeout = timeout
        self.tweets = {"id_str": [], 'text': [], 'created_at': []}

    def on_status(self, status):
        print("on status")
        if time() - self.started_at < self.timeout and len(self.tweets['id_str']) < self.max_tweets:
            print(len(self.tweets['id_str']) + 1)
            text = get_text_from_status(status)
            self.tweets['id_str'].append(status.id_str)
            self.tweets['text'].append(text)
            self.tweets['created_at'].append(status.created_at)
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

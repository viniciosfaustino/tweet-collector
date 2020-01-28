from time import time
import tweepy


class TweetListener(tweepy.StreamListener):
    def __init__(self, timeout: int, max_tweets: int):
        super(TweetListener, self).__init__()
        self.started_at = time()
        self.max_tweets = max_tweets
        self.timeout = timeout
        self.tweets = []

    def on_status(self, status):
        if time() - self.started_at < self.timeout and len(self.tweets) < self.max_tweets:
            # print_status_text(status)
            self.tweets.append(status.id_str)
        else:
            return False


def print_status_text(status):
    if hasattr(status, 'retweeted_status'):
        try:
            text = status.retweeted_status.extended_tweet["full_text"]
        except AttributeError:
            text = status.retweeted_status.text
    else:
        try:
            text = status.extended_tweet["full_text"]
        except AttributeError:
            text = status.text
    print(text)

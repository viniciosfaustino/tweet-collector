import os
import csv
import pandas as pd
import preprocessor as p
import re


def clear_tweets_from_csv(filepath: str):
    df = pd.read_csv(filepath)
    tweets = df[df.columns[0]]
    tweets = [p.clean(tweet) for tweet in tweets]
    tweets = [tweet.replace('"', '') for tweet in tweets]
    tweets = [re.sub(r'[^\w\s]', '', tweet) for tweet in tweets]
    df[df.columns[0]] = tweets
    path, name = os.path.split(filepath)
    new_name = os.path.splitext(name)[0] + "_clean.csv"
    new_filename = os.path.join(path, new_name)
    df.to_csv(new_filename, index=None)

clear_tweets_from_csv("/home/vinicios/reps/tweet-collector/data/ideacao/ideacao-suicida.csv")
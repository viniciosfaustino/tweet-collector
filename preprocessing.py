import os
import csv
import json
import re
import pandas as pd
import preprocessor as p


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


def save_unique(filepath: str):
    with open(filepath, 'r') as fp:
        file = json.load(fp)
        unique_texts = []
        unique_ids = []
        try:
            for i, text in enumerate(file['text']):
                if text not in unique_texts:
                    unique_texts.append(text)
                    unique_ids.append(file['id_str'][i])
            file['text'] = unique_texts
            file['id_str'] = unique_ids
            df = pd.DataFrame.from_dict(file)
            path, name = os.path.split(filepath)
            new_name = os.path.splitext(name)[0] + "_unique.csv"
            new_filename = os.path.join(path, new_name)
            df.to_csv(new_filename, index=None)
        except:
            pass

# clear_tweets_from_csv("/home/vinicios/reps/tweet-collector/data/ideacao/ideacao-suicida.csv")
# save_unique('/home/vinicios/reps/tweet-collector/data/ideacao/ideacao-Tue-Feb-18-22:00:41-2020.json')
import errno
import json
import logging
import os
import tweepy
from argparse import ArgumentParser
from typing import List
from time import ctime


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


def get_text_from_tweet_id(id_str: str, api):
    print(type(id_str))
    try:
        status = api.get_status(id_str, tweet_mode="extended")
        text = get_text_from_status(status)
        text = text.replace("\n", " ")
        return text

    except Exception as e:
        print("Error:", e['message'])
        raise Exception


def get_tracked_entities(path: str):
    with open(path, "r") as f:
        track = f.readlines()

    return [entity.strip("\n") for entity in track]


def load_args():
    parser = ArgumentParser()

    parser.add_argument("--track", required=True, type=str,
                        help="Text file with the things to track.")

    parser.add_argument("--name", required=True, type=str,
                        help="Name of the project.")

    parser.add_argument("--output_dir", required=True, type=str,
                        help="Output directory.")

    parser.add_argument("--max_tweets", type=int, default=100000,
                        help="Maximum number of tweets to collect.")

    parser.add_argument("--checkpoint_after", type=int, default=None,
                        help="Create a checkpoint file after collecting a determined number of tweets.")

    return parser.parse_args()


def process_status(status):
    print(status.text)
    #TODO


def get_tweets_from_user_id(user_id: str, api):
    for status in tweepy.Cursor(api.user_timeline, id=user_id).items():
        process_status(status)


def retrieve_text_from_json(filepath: str):
    print("retrieve started")
    with open(filepath, 'rb') as f:
        logging.info("json opened")
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


def save_tweets_to_file(path: str, name: str, tweets: List[str], id_only: bool = False):
    logging.info("Saving {} tweets to {}{}.".format(len(tweets["id_str"]), path, name))
    if not os.path.exists(path):
        os.mkdir(path)
    path = os.path.join(path, name)
    try:
        os.mkdir(path)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise
        pass

    created_at = ctime()
    created_at = created_at.replace(' ', '-')
    if id_only:
        data = {'name': name, 'created_at': created_at, "user_id": tweets["user_id"],
                "id_str": tweets['id_str'], 'hashtags': tweets['hashtags'], "mentions":  tweets['mentions']}

    else:
        data = {'name': name, 'created_at': created_at, "user_id": tweets["user_id"],
                "id_str": tweets['id_str'], 'text': tweets['text'], 'timestamp': tweets['timestamp'],
                'hashtags': tweets['hashtags'], "mentions":  tweets['mentions']}

    filename = name+"-"+str(created_at)+'.json'
    file = os.path.join(path, filename)

    with open(file, "w") as f:
        print("teje criado")
        json.dump(data, f, indent=4)

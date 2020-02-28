from tweetCollector import *
_track = ['covid19', 'coronavirus', 'covid-19']
collector = TweetCollector('covid19', track=_track)
collector.start_stream()
collector.save_tweets_to_file()

# get_text_from_status()

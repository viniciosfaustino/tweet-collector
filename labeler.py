import os
import json
import pandas as pd


def label(filepath: str, dataset_name: str = ''):
    with open(filepath, 'r') as f:
        data = json.load(f)
        labeled = {'tweets': [], 'y': []}
        for tweet in data['text']:
            print(tweet)
            print("1 - positive |  0 - negative")
            number = False
            while not number:
                try:
                    label = int(input())
                    number = True
                except:
                    print("must be 0 or 1")
            print('\n')
            labeled['tweets'].append(tweet)
            labeled['y'].append(label)
        output = os.path.split(filepath)[0]
        output = os.path.join(output, dataset_name+'.csv')

        df = pd.DataFrame.from_dict(labeled)
        df.to_csv(output)

label('data/ideacao/ideacao-Tue-Feb-18-22:00:41-2020.json', 'ideacao-suicida')



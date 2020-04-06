import json
from build_wc import *


def wordcloud_from_json(path: str, keywords: list, ext: str = 'png'):
    texts = []
    for file in os.listdir(path):
        if file.endswith('json'):
            with open(os.path.join(path, file), "r") as f:
                fp = json.load(f)

                text = fp['text']
                for t in text:
                    if t not in texts:
                        texts.append(t)

                name = os.path.splitext(file)[0]

                filename = name + '.' + ext
                try:
                    os.mkdir(os.path.join(path, 'wc2'))
                except:
                    pass

                build_cloud(texts, os.path.join(path, 'wc2'), filename, keywords)
import requests
import time
import json


base = "http://54.87.190.90//recommend_document"
def get_words(dat, raw_string):
    words = {}
    for a in dat.keys():
        semi_words = []
        for b in dat[a]['spans']:
            semi_words.append(raw_string[b[0]:b[1]])
        words[a] = semi_words
    return words

st = time.time()
# response = requests.post(base, json={
#     "recommend": 1,
#     "doc_id": 1,
#     "label": '3',
#     "new_label": "None",
#     "response_time": 5
# })
response=json.load(open('dataset.json'))
et = time.time()

elapsed_time = et - st
print(elapsed_time)
# print(response.json()["topic_keywords"])
# print(response.json()["topic_order"])
print(get_words(response["topic"], response["raw_text"]))
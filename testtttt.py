import requests
import time
import json
from xml.dom import minidom
import os



# def get_words(dat, raw_string):
#     words = {}
#     for a in dat.keys():
#         semi_words = []
#         for b in dat[a]['spans']:
#             try:
#                 semi_words.append(raw_string[b[0]:b[1]])
#             except:
#                 continue
#         words[a] = set(semi_words)
#     return words
# received_data = json.load(open('dataset.json'))

create_user = "http://54.87.190.90//create_user"
recommend_document = "http://54.87.190.90//recommend_document"

# # response=received_data
# st = time.time()

# user = requests.post(create_user, {
#     "user_session": "daniel"
#     })
# print(user.json())

response = requests.post(recommend_document, json={
    "document_id": '408',
    "label": '3',
    "response_time": '1',
    "user_id": 23
})
# # print(user.json()["user_id"])
# et = time.time()

# elapsed_time = et - st
# print(elapsed_time)
# data = response.json()
# print(data)
print(response.json())
# # print(response.json()["topic_order"])

# # print(response.json()["topic"])

# print(words("alt.atheism", data))
# print(response.json())
# print(respons)
# 
# print(get_words(data["topic"], data["raw_text"]))
# responses = []


def save_response(name, label, response_time, document_id, user_id):
    root = minidom.Document()
    xml = root.createElement('root')
    root.appendChild(xml)

    user_name = root.createElement('name')
    user_name.setAttribute("name", name)
    xml.appendChild(user_name)

    response_times = root.createElement('response_time')
    response_times.setAttribute("response_time", response_time)
    xml.appendChild(response_times)

    document_ids = root.createElement('document_id')
    document_ids.setAttribute("document_id", document_id)
    xml.appendChild(document_ids)

    labels = root.createElement('label')
    labels.setAttribute("label", label)
    xml.appendChild(labels)

    user_ids = root.createElement('user_id')
    user_ids.setAttribute("user_id", user_id)
    xml.appendChild(user_ids)

    xml_str = root.toprettyxml(indent ="\t")
    directory = "./static/"+name

    save_path_file = directory + "/"+ str(document_id) +".xml"
    try:
        os.makedirs(name)
    except:
        print("all_good")
    with open(save_path_file, "w") as f:
        f.write(xml_str)

    return xml_str

# print(save_response("daniel", "sports", "0.55", "1", "12"))








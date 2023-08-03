import re, numpy as np, pandas as pd
from pprint import pprint
import pickle
from xml.dom import minidom
import os


def read_data(path):
    return pd.read_json(path)

def filter_data(json_data, probability):
    filtered_topics = {}
    for a in json_data['topics']:
        results = json_data['topics'][a]
        each_file = pd.DataFrame(results)
        results = each_file[each_file['score']>=probability]
        filtered_topics[a]= {
            "spans": results['spans'].to_list(),
            "score": results['score'].to_list()
            }
    return filtered_topics


def get_words(dat, raw_string):
    words = {}
    for a in dat.keys():
        semi_words = []
        for b in dat[a]['spans']:
            try:
                semi_words.append(raw_string[b[0]:b[1]])
            except:
                continue
        words[a] = set(semi_words)
    return words


def highlight_words(text, words):
    for word in words:
        text = text.replace(word, f"<span style='background-color:yellow'>{word}</span>")
    return text


def save_response(name, label, response_time, document_id, user_id):
    root = minidom.Document()
    xml = root.createElement('root')
    root.appendChild(xml)

    user_name = root.createElement('name')
    user_name.setAttribute("name", name)
    xml.appendChild(user_name)

    response_times = root.createElement('response_time')
    response_times.setAttribute("response_time", str(response_time))
    xml.appendChild(response_times)

    document_ids = root.createElement('document_id')
    document_ids.setAttribute("document_id", str(document_id))
    xml.appendChild(document_ids)

    labels = root.createElement('label')
    labels.setAttribute("label", label)
    xml.appendChild(labels)

    user_ids = root.createElement('user_id')
    user_ids.setAttribute("user_id", str(user_id))
    xml.appendChild(user_ids)

    xml_str = root.toprettyxml(indent ="\t")

    directory = "./static/"+name

    save_path_file = directory + "/"+ str(document_id) +".xml"
    try:
        os.makedirs(directory)
    except:
        print("all_good")
    with open(save_path_file, "w") as f:
        f.write(xml_str)


    return xml_str


def get_texts (topic_list, all_texts):
    results = {}
    for a in topic_list["cluster"].keys():
        sub_results = {}
        for b in topic_list["cluster"][a]:
            sub_results[str(b)] = all_texts["text"][str(b)]
        results[a]= sub_results
    return results

def get_sliced_texts(topic_list, all_texts):
    results = {}
    for a in topic_list["cluster"].keys():
        sub_results = {}
        for b in topic_list["cluster"][a][:6]:
            sub_results[str(b)] = all_texts["text"][str(b)]
        results[a]= sub_results
    return results

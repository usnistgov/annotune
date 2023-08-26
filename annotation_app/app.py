from flask import Flask, request, render_template, url_for, redirect, flash, session
import numpy as np
import pandas as pd
from .tools import *
import json
from flask_session import Session
from xml.dom import minidom
import requests
import time
from datetime import datetime
import os
import ast
import random


received_data = json.load(open('dataset.json'))




os.urandom(24).hex()

topic_list = json.load(open('topic_list.json'))
all_texts = json.load(open("congressional_bills.json"))
# url = 'https://nist-topic-model.umiacs.umd.edu'
# url = "https://nist-topic-model.umiacs.umd.edu"
# url = "http://54.87.190.90:5001"
url = "http://127.0.0.1:8820"

# global predicitons
global skip
# predictions = []


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24).hex()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


## uSER FIRST LOGS IN

@app.route("/")
def home():
    return redirect(url_for("login"))


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method =="POST":
        with open('./static/users/users.json') as user_file:
            name_string = user_file.read()
            names = json.loads(name_string)
        name = request.form["name"]
        # email = request.form["email"]

        identity = name
        session["name"] = identity
        session['time_started'] = True
        session["begin"] = datetime.now()
        # print(session["begin"])
        session["start_time"] = ""
        

        if identity in list(names.keys()):
            session["name"] = names[identity]['username']
            session["labels"] = names[identity]["labels"]
            session["user_id"] = names[identity]["id"]
            session["labelled_document"] = names[identity]["labelled_document"]
            
            user_id = session["user_id"]
            print('user id is {}'.format(user_id))
            # save_time(session["name"], "home_page")
            return redirect(url_for("home_page", name=identity, user_id=user_id))
            # return redirect(url_for("active_check", name=identity))
            
        else:
            user = requests.post(url + "//create_user", {"user_session": identity})
            print(user)
            user_id = user.json()["user_id"] 
            session["user_id"] = user_id
            session["labels"] = ""
            session["labelled_document"] = ""
            data = {
                "username": identity, 
                "id" : user_id,
                "labels" : session["labels"],
                "labelled_document" : session["labelled_document"]
            }

            session["user_id"] = user_id  
            names[identity]=data
            
            with open('./static/users/users.json', mode='w', encoding='utf-8') as name_json:
                # names = json.loads(name_string)
                names[identity] = data
                json.dump(names, name_json, indent=4)

            try:
                make_folder(identity)
            except:
                pass
            save_first_time(session["name"], "home_page")
            
            return redirect(url_for("home_page", name=identity, user_id=user_id))
    return render_template("login.html") 




# READING WHAT THE STUDY IS ABOUT
@app.route("//firstpage//<name>/", methods = ["POST", "GET"])
def home_page(name):
    if session.get("name") != name:
        # if not there in the session then redirect to the login page
        return redirect("/login")
    if request.method =="POST":
        if session["time_started"] == True:
            session["begin"] = datetime.now()
            session["time_started"] = False
        save_time(session["name"], "to_list")



        return redirect(url_for("active_check", name=name))
    return render_template("first.html", name=name, time=session["begin"])



@app.route("//checkactive//<name>//", methods=["POST", 'GET'])
def active_check(name):
    if session.get("name") != name:
        # if not there in the session then redirect to the login page
        return redirect("/login")

    get_topic_list = url + "//get_topic_list"
    topics = requests.post(get_topic_list, json={
                            "user_id": session['user_id']
                            }).json()
    if len(topics["cluster"].keys()) == 1:
        session["is_active"] = 1
        return redirect(url_for("active_list", name=name, time=session["begin"]))
    else:
        session["is_active"] = 0
        return redirect(url_for("non_active_list", name=name, time=session["begin"]))





@app.route("//active_list//<name>", methods=["POST", "GET"])
def active_list(name):
    if session.get("name") != name:
    # if not there in the session then redirect to the login page
        return redirect("/login")

    get_topic_list = url + "//get_topic_list"
    topics = requests.post(get_topic_list, json={
                            "user_id": session['user_id']
                            }).json()
    save_time(session["name"], "active_list")


    rec = str(topics["document_id"])
    docs = list(set(session["labelled_document"].strip(",").split(",")))
    
    docs_len= len(docs)

    results = get_single_document(topics["cluster"]["1"], all_texts, docs)



    # print(len(topics["cluster"]["1"]))

    session["rec_block"] = [x for x in topics["cluster"]["1"] if x != rec]
    print(session["rec_block"])
    

    elapsed_time = datetime.now() - session["begin"]
    secs = round(elapsed_time.total_seconds())

    if request.method =="POST":
        return redirect(url_for("finish"))
    return render_template("active_list.html", results=results, name=name, rec = rec , docs_len=docs_len, elapsed_time=str(elapsed_time), secs=secs)


 
 
@app.route("//non_active_list//<name>", methods=["POST", "GET"])
def non_active_list(name):
    if session.get("name") != name:
        # if not there in the session then redirect to the login page
        return redirect("/login")

    get_topic_list = url + "//get_topic_list" 
        # print(session)
    topics = requests.post(get_topic_list, json={
                            "user_id": session['user_id']
                            }).json()

    recommended = int(topics["document_id"])

    save_time(session["name"], "non_active_list")



    docs = list(set(session["labelled_document"].strip(",").split(",")))
    docs_len = len(docs)
    # print(recommended)

    recommended_topic, recommended_block = get_recommended_topic(recommended, topics, all_texts)

    results = get_texts(topic_list=topics, all_texts=all_texts, docs=docs)

    sliced_results = get_sliced_texts(topic_list=topics, all_texts=all_texts, docs=docs)
 
    keywords = topics["keywords"] 
    elapsed_time = datetime.now() - session["begin"]
    secs = round(elapsed_time.total_seconds())
    all_available_documents = [list(results[t].keys()) for t in [p for p in list(results.keys())]]
    long_list = []
    for y in all_available_documents:
        for e in y:
            long_list.append(e)
    # print(long_list)

    session["rec_block"] = list(recommended_block[list(recommended_block.keys())[0]].keys()) + long_list
    print(session['rec_block'])

    if request.method =="POST":
        return redirect(url_for("finish"))

    return render_template("nonactive.html", sliced_results=sliced_results, results=results, name=name, keywords=keywords, recommended=str(recommended), document_list = topics["cluster"], docs_len = docs_len, recommended_block=recommended_block, recommended_topic=recommended_topic, elapsed_time=str(elapsed_time), secs=secs)

 
@app.route("//active//<name>//<document_id>", methods=["GET", "POST"])
def active(name, document_id):

    text = all_texts["text"][str(document_id)]

    session["start_time"] = str(session["start_time"]) + "+" + str(datetime.now().strftime("%H:%M:%S"))

    labels = list(set(session["labels"].strip(",").split(",")))
    docs = list(set(session["labelled_document"].strip(",").split(",")))
    docs_len = len(docs)
    total = len(all_texts["text"])

    elapsed_time = datetime.now() - session["begin"]
    secs = round(elapsed_time.total_seconds())
    save_time(session["name"], str(document_id))

    skip = random.choice([x for x in session["rec_block"] if x != document_id])

    if request.method =="POST":
        label = request.form.get("label").lower()
        drop = request.form.get("suggestion").lower()

        label = str(drop) + str(label)
        name=name
        document_id=document_id
        user_id = session["user_id"]

        st = datetime.strptime(session["start_time"].strip("+").split("+")[-2], "%H:%M:%S")
        et = datetime.strptime(session["start_time"].strip("+").split("+")[-1], "%H:%M:%S")

        response_time = str(et-st)
        elapsed_time = datetime.now() - session["begin"]
        secs = round(elapsed_time.total_seconds())
        
        save_response(name, label, response_time, document_id, user_id)
        recommend_document = url + "//recommend_document"
        posts = requests.post(recommend_document, json={
        "user_id" : int(user_id),
        "label": label,
        "response_time": response_time,
        "document_id" : document_id}).json()
        print(posts)
        next = posts["document_id"]
        # print(posts.keys())
        predictions.append(label.lower()) 
        
        # session["labelled_document"] = session["labelled_document"]+","+str(document_id)
        session["labels"] = session["labels"] + "," + label
        labels = list(set(session["labels"].strip(",").split(",")))
        # print(labels)
        session["labelled_document"] = session["labelled_document"]+","+str(document_id)
        save_labels(session)
        docs = list(set(session["labelled_document"].strip(",").split(",")))
        docs_len = len(docs)
         # print(label) 
        flash("Response has been submitted")
        save_time(session["name"], str(document_id)+"labelled")
        
        return redirect(url_for("active", name=name, document_id=next, predictions=labels, docs_len = docs_len, total=total, elapsed_time=str(elapsed_time), secs=secs, skip=skip))
    return render_template("activelearning.html", text =text, predictions=labels, docs_len=docs_len, document_id=document_id, total=total,elapsed_time=str(elapsed_time), secs=secs, skip=skip)

    

 


### lABELLING THE TOPIC AND SAVING THE RESPONSE aaa
@app.route("//get_label//<document_id>//", methods=["POST", 'GET'])
def get_label(document_id):
    document_id = document_id 
    user_id=session["user_id"] 
    get_document_information = url + "//get_document_information"
    data = requests.post(get_document_information, json={ "document_id": document_id,
                                                        "user_id":user_id
                                                         }).json()
    save_time(session["name"], "relabel")

                                                         
    return redirect( url_for("label", response=data, name=session["name"], document_id=document_id))
    




@app.route("/logout", methods=["POST", "GET"])
def finish():
    name = session['name']
    save_time(session["name"], "finish")
    session.pop(name, None)
    return redirect(url_for("login"))



@app.before_request
def require_login():
    allowed_route = ['login']
    if request.endpoint not in allowed_route and "name" not in session:
        return redirect('/login')



@app.route('//non_active_label//<name>//<document_id>/', methods=["POST", "GET"])
def non_active_label(name, document_id):
    get_document_information = url + "//get_document_information"
    response = requests.post(get_document_information, json={ "document_id": document_id,
                                                        "user_id":session["user_id"]
                                                         }).json()
                                                         

    text = all_texts["text"][str(document_id)]
    words = get_words(response["topic"],  text)
    labels = list(set(session["labels"].strip(",").split(",")))
    session["start_time"] = str(session["start_time"]) + "+" + str(datetime.now().strftime("%H:%M:%S"))
    
    elapsed_time = datetime.now() - session["begin"]
    secs = round(elapsed_time.total_seconds())
    

    total = len(all_texts["text"].keys())
    docs = list(set(session["labelled_document"].strip(",").split(",")))
    docs_len = len(docs)
    
    skips = random.choice([x for x in session["rec_block"] if x != document_id])



    if request.method =="POST":
        label = request.form.get("label").lower()
        drop = request.form.get("suggestion").lower()
        label = str(drop)+str(label)

        name=name 
        document_id=str(document_id)
        user_id = session["user_id"]

        st = datetime.strptime(session["start_time"].strip("+").split("+")[-2], "%H:%M:%S")
        et = datetime.strptime(session["start_time"].strip("+").split("+")[-1], "%H:%M:%S")

        response_time = str(et-st)

        elapsed_time = datetime.now() - session["begin"]
        secs = round(elapsed_time.total_seconds())
        recommend_document = "https://nist-topic-model.umiacs.umd.edu/recommend_document"
        recommend_document = url + "//recommend_document"
        posts = requests.post(recommend_document, json={
        "user_id" : int(user_id),
        "label": label,
        "response_time": str(response_time),
        "document_id" : document_id
        }).json()

        next = posts["document_id"]
        predictions.append(label.lower())
        # print(posts["prediction"])
        
        
        session["labelled_document"] = session["labelled_document"]+","+str(document_id)
        docs = list(set(session["labelled_document"].strip(",").split(",")))
        session["labels"] = session["labels"] + "," + label
        labels = list(set(session["labels"].strip(",").split(",")))
        docs_len = len(docs)
        save_labels(session)

        save_response(name, label, response_time, document_id, user_id)
        get_document_information = url + "//get_document_information"
        response = requests.post(get_document_information, json={ "document_id": posts["document_id"],
                                                        "user_id":session["user_id"]
                                                         }).json()
    
        flash("Response has been submitted")
        save_time(session["name"], str(document_id)+"finish")
        total = len(all_texts["text"].keys())
        done = len(docs)
        return redirect(url_for("non_active_label", response=response, words=words, document_id=posts["document_id"], name=name, predictions=labels, pred=response["prediction"], total=total, docs_len=docs_len, elapsed_time=str(elapsed_time)[:7], secs = secs, skips=skips))

    return render_template("nonactivelabel.html", response=response, words=words, document_id=document_id, text=text, name=name, predictions=labels, pred=response["prediction"], total=total, docs_len=docs_len, elapsed_time=str(elapsed_time)[:7], secs = secs, skips=skips)

  
@app.route("/try")  
def trial():
    return render_template("try.html")





@app.route("/non_active/<name>/<topic_id>//<documents>//<keywords>")
def topic(name, topic_id, documents, keywords): 
    # print(topic_id)
    # res = get_single_document(documents, all_texts)
    keywords = keywords.strip("'[]'").split("', '")
    docs = list(set(session["labelled_document"].strip(",").split(",")))
    docs_len = len(docs)
    
    res = get_single_document(documents.strip("'[]'").split(", "), all_texts, docs=docs)

    return  render_template("topic.html", res = res, topic_id=topic_id, docs_len = docs_len, keywords=keywords) 
 
 

@app.route("/<name>/labeled/<document_id>")
def view_labeled(name,document_id):
    text = all_texts["text"][document_id]
    response = extract_label(name, document_id )
    
    return render_template("viewlabeled.html", text=text, response=response, document_id=document_id) 



@app.route("/<name>/labeled_list/")
def labeled_list(name):
    labe = session["labelled_document"]
    docs = list(set(session["labelled_document"].strip(",").split(",")))
    docs_len = len(docs)
    docss = labelled_docs(labe, all_texts)
    completed = completed_json_(name)
    completed_docs = get_completed(completed, all_texts)
    elapsed_time = datetime.now() - session["begin"]
    secs = round(elapsed_time.total_seconds())
    return render_template("completed.html", completed_docs=completed_docs, docss=docss, secs=secs, elapsed_time=str(elapsed_time), docs_len=docs_len)
 

@app.route("/<name>/edit_response/<document_id>")
def edit_labels(name, document_id):
    if session["is_active"] == True:
        return redirect(url_for("active", name=name, document_id=document_id))

    if session["is_active"] == False:
        return redirect(url_for("non_active_label", name=name, document_id=document_id))


@app.route("/modal")
def modal():
    return render_template("modal.html")

    
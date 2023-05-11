from flask import Flask, request, render_template, url_for, redirect, flash, session
import numpy as np
import pandas as pd
from .tools import *
import json
from flask_session import Session
# from flask_restful import API, Resource
from xml.dom import minidom
import requests
import time
import os
from flask import jsonify
import ast


received_data = json.load(open('dataset.json'))


os.urandom(24).hex()

topic_list = json.load(open('topic_list.json'))
all_texts = json.load(open("newsgroup_sub_500.json"))
base = "http://54.87.190.90//recommend_document"


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24).hex()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


## uSER FIRST LOGS IN

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method =="POST":
        name = request.form["name"]
        session["name"] = name
        user = requests.post("https://nist-topic-model.umiacs.umd.edu//create_user", {"user_session": session["name"]})

        user_id = user.json()["user_id"]
        session["user_id"] = user_id
        return redirect(url_for("home_page", name=name, user_id=user_id))
    return render_template("login.html")




# READING WHAT THE STUDY IS ABOUT
@app.route("/firstpage/<name>/<user_id>", methods = ["POST", "GET"])
def home_page(name, user_id):
    # print(session)
    if session.get("name") != name:
        # if not there in the session then redirect to the login page
        return redirect("/login")

    if request.method =="POST":

        return redirect(url_for("topic_page", name=name))
        
    return render_template("first.html", name=name)


  
# @app.route("/initial", methods=["POST", "GET"])
# def initial_request():
#     recommend_document = "http://54.87.190.90//recommend_document"
#     data = requests.post(recommend_document, json={
#             "document_id": "-1",
#             "label": '3',
#             "response_time": '1',
#             "user_id":session["id"]
#             })
#     # print(data.json())

#     global response 
#     response=data.json()
#     return redirect(url_for('topic_page', name=session['name'], response=response))


## lIST OF TOPICS BASED ON THE SELECTED LIST
@app.route("/topic/<name>", methods = ["POST", "GET"])
def topic_page(name):
    
    if "name" in session:
        get_topic_list = "http://54.87.190.90//get_topic_list"
        # print(session)
        topics = requests.post(get_topic_list, json={
                            "user_id": 5
                            }).json()

        results = get_texts(topic_list=topics, all_texts=all_texts)

        if request.method =="POST":
            return redirect(url_for("finish"))
 
        return render_template("state1.html", results=results, name=name)
    return render_template("login.html")



### lABELLING THE TOPIC AND SAVING THE RESPONSE



@app.route("/get_label/<document_id>/", methods=["POST", 'GET'])
def get_label(document_id):
    document_id = document_id 
    user_id=session["user_id"] 
    get_document_information = "https://nist-topic-model.umiacs.umd.edu/get_document_information"
    data = requests.post(get_document_information, json={ "document_id": document_id,
                                                        "user_id":user_id
                                                         }).json()
    print(session)

    return redirect( url_for("label", response=data, name =session["name"], document_id=document_id))
    




@app.route("/logout", methods=["POST", "GET"])
def finish():
    name = session['name']
    session.pop(name)
    return redirect(url_for("login"))



@app.before_request
def require_login():
    allowed_route = ['login']
    if request.endpoint not in allowed_route and "name" not in session:
        return redirect('/login')




@app.route('/label/<name>/<document_id>/<response>/', methods=['POST', 'GET'])
def label(name,document_id, response):
    
    st = time.time()
    response = ast.literal_eval(response)



    print(response)
    text = all_texts["text"][str(document_id)]

    if request.method =="POST":
        name=name
        document_id=document_id
        user_id = session["user_id"]
        et = time.time()
        response_time = st- et
        label = request.form.get("label")

        save_response(name, label, response_time, document_id, user_id)
    

        return redirect(url_for("topic_page", name=name, response=response))

    words = get_words(response["topic"],  text)

    return render_template("label.html", response=response, words=words, document_id=document_id, text=text)







# @app.route('/', methods=['POST', 'GET'])
# def get_data():
#     global response 
#     global counter
#     id = response["document_id"]
#     new_label = None
#     label=None
#     st = time.time()
#     et=time.time()
#     text = response["raw_text"]
#     # word_dict = get_words(response["topic"], response["raw_text"])
#     # text = highlight_words(text, word_dict["8"])
#     words = get_words(response["topic"], response["raw_text"])

#     if request.method=="POST":

        
#         et = time.time()
#         # label = str(request.form["all_topics"])
#         new_label = request.form["newlabel"]
#         response_time = et -st
        

#         if label and new_label:
#             flash('You cannot select an old label and a new label!')


#         elif not label and not new_label:
#             flash('Please select a label or enter a new label!')


#         else:
#             if len(new_label) == 0:
#                 new_label ="None"
        
#             if len(str(label))==0:
#                 label = "None"

#             response = requests.post(base, json={"document_id": str(id), "label": label, "response_time": str(response_time)}).json()
#             text = response["raw_text"]

#             print(response_time)

            
#             return render_template("index.html", text=text, received_data=response, words=words, counter=counter)
                
#     return render_template("index.html", text=text, received_data=response, words=words, counter=counter)
    



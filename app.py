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
url = 'https://nist-topic-model.umiacs.umd.edu'
# url = 'http://localhost:5000'


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
        name = request.form["name"]
        session["name"] = name
        user = requests.post(url + "//create_user", {"user_session": session["name"]})

        user_id = user.json()["user_id"]
        
        print('user id is {}'.format(user_id))
        session["user_id"] = user_id


        return redirect(url_for("home_page", name=name, user_id=user_id))
    return render_template("login.html")




# READING WHAT THE STUDY IS ABOUT
@app.route("//firstpage//<name>/", methods = ["POST", "GET"])
def home_page(name):
    # print(session)
    if session.get("name") != name:
        # if not there in the session then redirect to the login page
        return redirect("/login")

    if request.method =="POST":

        return redirect(url_for("active_check", name=name))
        
    return render_template("first.html", name=name)



@app.route("//checkactive//<name>//", methods=["POST", 'GET'])
def active_check(name):
    if session.get("name") != name:
        # if not there in the session then redirect to the login page
        return redirect("/login")

    get_topic_list = url + "//get_topic_list"
        # print(session)
    topics = requests.post(get_topic_list, json={
                            "user_id": session['user_id']
                            }).json()

    # print(topics)  
    if len(topics["cluster"].keys()) == 1:

        return redirect(url_for("active_list", name=name))

    else:
        return redirect(url_for("non_active_list", name=name))







@app.route("//active_list//<name>", methods=["POST", "GET"])
def active_list(name):
    if session.get("name") != name:
    # if not there in the session then redirect to the login page
        return redirect("/login")

    get_topic_list = url + "//get_topic_list"
        # print(session)
    topics = requests.post(get_topic_list, json={
                            "user_id": session['user_id']
                            }).json()
    # print(topics)
    recommended = int(topics["document_id"])
    print(recommended)

    results = get_texts(topic_list=topics, all_texts=all_texts)

    if request.method =="POST":
        return redirect(url_for("finish"))
 
    return render_template("active_list.html", results=results, name=name, recommeded=recommended)

    


 
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

    results = get_texts(topic_list=topics, all_texts=all_texts)

    sliced_results = get_sliced_texts(topic_list=topics, all_texts=all_texts)
    print(sliced_results)

    keywords = topics["keywords"] 
    # print(keywords)

    if request.method =="POST":
        return redirect(url_for("finish"))

    return render_template("nonactive.html",sliced_results=sliced_results, results=results, name=name, keywords=keywords, recommended=recommended)



@app.route("//acitve//<name>//<document_id>", methods=["GET", "POST"])
def active(name, document_id):
    get_topic_list = url + "//get_topic_list"

    topics = requests.post(get_topic_list, json={
                            "user_id": session['user_id']
                            }).json()

    results = get_texts(topic_list=topics, all_texts=all_texts)
    text = all_texts["text"][str(document_id)]
    st =time.time()
    if request.method =="POST":
        name=name
        document_id=document_id
        user_id = session["user_id"]
        et = time.time()
        response_time = st- et
        label = request.form.get("label")

        save_response(name, label, response_time, document_id, user_id)
    

        return redirect(url_for("active_list", name=name))
    return render_template("activelearning.html", text =text ) 

    




### lABELLING THE TOPIC AND SAVING THE RESPONSE aaa



@app.route("//get_label//<document_id>//", methods=["POST", 'GET'])
def get_label(document_id):
    document_id = document_id 
    user_id=session["user_id"] 
    get_document_information = url + "//get_document_information"
    data = requests.post(get_document_information, json={ "document_id": document_id,
                                                        "user_id":user_id
                                                         }).json()
                                                         


    return redirect( url_for("label", response=data, name =session["name"], document_id=document_id))
    




@app.route("/logout", methods=["POST", "GET"])
def finish():
    name = session['name']
    session.pop(name, None)
    return redirect(url_for("login"))



@app.before_request
def require_login():
    allowed_route = ['login']
    if request.endpoint not in allowed_route and "name" not in session:
        return redirect('/login')



@app.route('//non_active_label//<name>//<document_id>', methods=["POST", "GET"])
def non_active_label(name, document_id):
    st = time.time()
    get_document_information = url + "//get_document_information"
    response = requests.post(get_document_information, json={ "document_id": document_id,
                                                        "user_id":session["user_id"]
                                                         }).json()

    text = all_texts["text"][str(document_id)]
    words = get_words(response["topic"],  text)

    if request.method =="POST":
        name=name 
        document_id=document_id
        user_id = session["user_id"]
        et = time.time()
        response_time = st- et
        label = request.form.get("label")

        save_response(name, label, response_time, document_id, user_id)
    

        return redirect(url_for("non_active_list", name=name))


    return render_template("nonactivelabel.html", response=response, words=words, document_id=document_id, text=text)

  
@app.route("/try")
def trial():
    return render_template("try.html")


# @app.route("view_all//<name>//<topic>")
# def view_all(name, topic):

    
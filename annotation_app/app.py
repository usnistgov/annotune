from flask import Flask, request, render_template, url_for, redirect, flash, session
import numpy as np
import pandas as pd
from .utils import *
import json
from xml.dom import minidom
import requests
import time
from datetime import datetime, timezone
import os
import ast
import random
from flask_session import Session



received_data = json.load(open('dataset.json'))




os.urandom(24).hex()

# topic_list = json.load(open('topic_list.json'))
all_texts = json.load(open("congressional_bill_train.json"))
url = "http://127.0.0.1:8820"

global predicitons
global skip
predictions = []


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24).hex()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)


## uSER FIRST LOGS IN

@app.route("/")
def home():
    """
    Handle the root route ("/") of the annotation application.
    Redirects the user to the login page.
    """
    return redirect(url_for("login"))


@app.route("/login", methods=["POST", "GET"])
def login():

    """
    Handles user login functionality for the application.

    If the request method is POST:
    - Reads user data from JSON files.
    - Validates the submitted user name.
    - If the user is valid, sets session variables for the user, including name, user ID, labels, and labeled documents.
    - Redirects the validated user to the home page.
    - If the user is not valid, redirects back to the login page.

    If the request method is GET:
    - Renders the login page template.

    Routes:
    - GET: '/'
    - POST: '/login'

    Method:
    - GET
    - POST

    Parameters:
    - None

    Returns:
    - If the request method is POST and the user is validated, it redirects to the home page ('/firstpage/<name>/').
    - If the request method is POST and the user is not validated, it redirects back to the login page ('/login').
    - If the request method is GET, it renders the login page template ('login.html').
    """


    if request.method =="POST":
        with open('./static/users/users.json') as user_file:
            name_string = user_file.read()
            names = json.loads(name_string)

        with open('./static/users/specified_users.json') as user_file:
            namess = user_file.read()
            specified_names = json.loads(namess)


        name = request.form["name"]
        # email = request.form["email"]

        if name not in specified_names.keys():
            return redirect("/login")

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
            # print('user id is {}'.format(user_id))
            # save_time(session["name"], "home_page")
            return redirect(url_for("home_page", name=identity, user_id=user_id))
            # return redirect(url_for("active_check", name=identity))
            
        else:
            user = requests.post(url + "//create_user", {"user_session": identity})
            # print(user)
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
            save_first_time(session["name"], "homepage")
            
            return redirect(url_for("home_page", name=identity, user_id=user_id))
    return render_template("login.html") 




# READING WHAT THE STUDY IS ABOUT
@app.route("//firstpage//<name>/", methods = ["POST", "GET"])
def home_page(name):
    """
    Handles the user's home page functionality in the Flask application.

    Parameters:
    - name (str): The name of the user, extracted from the URL.

    Returns:
    - If the user is not logged in (name not in session), redirects to the login page ('/login').
    - If the request method is POST and the user's session has just started, updates the session start time.
    - If the request method is POST, redirects to the active check page ('/active_check/<name>/').
    - If the request method is GET, renders the home page template ('first.html') with user name and session start time.
    
    Routes:
    - GET: '/firstpage/<name>/'
    - POST: '/firstpage/<name>/'
    
    Method:
    - GET
    - POST

    """
    if session.get("name") != name:
        # if not there in the session then redirect to the login page
        return redirect("/login")
    if request.method =="POST":
        if session["time_started"] == True:
            session["begin"] = datetime.now()
            session["time_started"] = False
        save_time(session["name"], "start")



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
    """
    Checks if the model being used is active learning or not.

    Parameters:
    - name (str): The name of the user, extracted from the URL.

    Returns:
    - If the user is not logged in (name not in session), redirects to the login page ('/login').
    - Retrieves the topic list for the user.
    - If there is only one topic in the topic list, marks the user as active and redirects to the active list page ('/active_list/<name>/').
    - If there are multiple topics in the topic list, marks the user as non-active and redirects to the non-active list page ('/non_active_list/<name>/').

    Routes:
    - GET/POST: '/checkactive/<name>/'
    
    Method:
    - GET
    - POST
    """
    save_time(session["name"], "selecting documents to label")
    if session.get("name") != name:
    # if not there in the session then redirect to the login page
        return redirect("/login")

    get_topic_list = url + "//get_topic_list"
    topics = requests.post(get_topic_list, json={
                            "user_id": session['user_id']
                            }).json()
    


    rec = str(topics["document_id"])
    docs = list(set(session["labelled_document"].strip(",").split(",")))
    
    docs_len= len(docs)

    results = get_single_document(topics["cluster"]["1"], all_texts, docs)

    session["rec_block"] = [x for x in topics["cluster"]["1"] if x != rec]

    elapsed_time = datetime.now() - session["begin"]
    secs = round(elapsed_time.total_seconds())
    save_time(session["name"], "active_list")
    if request.method =="POST":
        return redirect(url_for("finish"))
    return render_template("active_list.html", results=results, name=name, rec = rec , docs_len=docs_len, elapsed_time=str(elapsed_time), secs=secs)


 
 
@app.route("//non_active_list//<name>", methods=["POST", "GET"])
def non_active_list(name):
    save_time(session["name"], "selecting document to label")
    if session.get("name") != name:
        # if not there in the session then redirect to the login page
        return redirect("/login")

    get_topic_list = url + "//get_topic_list" 
    
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
    # print(session['rec_block'])

    if request.method =="POST":
        return redirect(url_for("finish"))

    return render_template("nonactive.html", sliced_results=sliced_results, results=results, name=name, keywords=keywords, recommended=str(recommended), document_list = topics["cluster"], docs_len = docs_len, recommended_block=recommended_block, recommended_topic=recommended_topic, elapsed_time=str(elapsed_time), secs=secs)

 
@app.route("//active//<name>//<document_id>", methods=["GET", "POST"])
def active(name, document_id):
    """
    Handles the non-active list functionality for the user in the Flask application.

    Parameters:
    - name (str): The name of the user, extracted from the URL.

    Returns:
    - If the user is not logged in (name not in session), redirects to the login page ('/login').
    - Retrieves the topic list for the user and the recommended document ID.
    - Saves the time when the user starts selecting a document to label.
    - Retrieves the user's labeled documents and relevant texts based on the topic list.
    - Prepares the data for rendering the non-active list page template ('nonactive.html').
    
    Routes:
    - GET: '/non_active_list/<name>'
    - POST: '/non_active_list/<name>'

    Method:
    - GET
    - POST
    """
    save_time(session["name"], str(document_id))
    save_time(session["name"], "labeling a document")
    text = all_texts["text"][str(document_id)]

    session["start_time"] = str(session["start_time"]) + "+" + str(datetime.now().strftime("%H:%M:%S"))

    labels = list(set(session["labels"].strip(",").split(",")))
    docs = list(set(session["labelled_document"].strip(",").split(",")))
    docs_len = len(docs)
    total = len(all_texts["text"])

    elapsed_time = datetime.now() - session["begin"]
    secs = round(elapsed_time.total_seconds())
    

    skip = random.choice([x for x in session["rec_block"] if x != document_id])

    get_document_information = url + "//get_document_information"
    response = requests.post(get_document_information, json={ "document_id": document_id,
                                                        "user_id":session["user_id"]
                                                         }).json()

        
    pred = response["prediction"].strip(",").split(',')

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
        # print(posts)
        next = posts["document_id"]
        # print(posts.keys())
        predictions.append(label.lower()) 
        # print(posts.keys())
        
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


        get_document_information = url + "//get_document_information"
        response = requests.post(get_document_information, json={ "document_id": posts["document_id"],
                                                        "user_id":session["user_id"]
                                                         }).json()

        pred = response["prediction"].strip(",").split(',')
        # print(response['prediction'])

        
        return redirect(url_for("active", name=name, document_id=next, predictions=labels, docs_len = docs_len, total=total, elapsed_time=str(elapsed_time), secs=secs, skip=skip, pred=pred))
    return render_template("activelearning.html", text =text, predictions=labels, docs_len=docs_len, document_id=document_id, total=total,elapsed_time=str(elapsed_time), secs=secs, skip=skip, pred=pred)

    

 


### lABELLING THE TOPIC AND SAVING THE RESPONSE aaa
@app.route("//get_label//<document_id>//", methods=["POST", 'GET'])
def get_label(document_id):
    """
    Handles the functionality to retrieve document labels in the Flask application.

    Parameters:
    - document_id (str): The ID of the document to retrieve labels for, extracted from the URL.

    Returns:
    - If the user is not logged in (name not in session), redirects to the login page ('/login').
    - Retrieves information about the specified document using its ID and the user ID.
    - Saves the time when the user starts relabeling the document.
    - Redirects to the label page to allow the user to add or edit labels for the document.

    Routes:
    - GET/POST: '/get_label/<document_id>'

    Method:
    - GET
    - POST
    """
    document_id = document_id 
    user_id=session["user_id"] 
    get_document_information = url + "//get_document_information"
    data = requests.post(get_document_information, json={ "document_id": document_id,
                                                        "user_id":user_id
                                                         }).json()
    save_time(session["name"], "relabel")
    save_time(session["name"], str(document_id))

                                                         
    return redirect( url_for("label", response=data, name=session["name"], document_id=document_id))
    




@app.route("/logout", methods=["POST", "GET"])
def finish():
    """
    Handles the user logout functionality in the Flask application.

    Returns:
    - If the user is not logged in (name not in session), redirects to the login page ('/login').
    - Saves the time when the user finishes the session.
    - Removes the user's session data and redirects to the login page.
    
    Routes:
    - GET/POST: '/logout'

    Method:
    - GET
    - POST
    """
    name = session['name']
    save_time(session["name"], "finish")
    session.pop(name, None)
    return redirect(url_for("login"))



@app.before_request
def require_login():
    """
    Checks if the user is logged in before processing any request.

    If the user is not logged in and the requested endpoint is not allowed (e.g., 'login'),
    redirects to the login page.

    Routes Allowed Without Login:
    - 'login'

    Returns:
    - If the user is not logged in and the requested endpoint is not allowed, redirects to the login page ('/login').
    """
    allowed_route = ['login']
    if request.endpoint not in allowed_route and "name" not in session:
        return redirect('/login')



@app.route('//non_active_label//<name>//<document_id>/', methods=["POST", "GET"])
def non_active_label(name, document_id):
    """
    Handles the labeling functionality for non-active documents in the Flask application.

    Parameters:
    - name (str): The name of the user, extracted from the URL.
    - document_id (str): The ID of the document to label, extracted from the URL.

    Returns:
    - If the user is not logged in (name not in session), redirects to the login page ('/login').
    - Retrieves information about the specified document using its ID and the user ID.
    - Saves the time when the user starts labeling the document.
    - Handles form submission to process the user's label input.
    - Redirects to the non-active label page with updated information after processing the label input.

    Routes:
    - GET/POST: '/non_active_label/<name>/<document_id>'

    Method:
    - GET
    - POST
    """
    save_time(session["name"], "labelling document")
    save_time(session["name"], str(document_id))

    get_document_information = url + "//get_document_information"
    response = requests.post(get_document_information, json={ "document_id": document_id,
                                                        "user_id":session["user_id"]
                                                         }).json()

    # print(response["prediction"])                      

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
        recommend_document = url + "//recommend_document"
        posts = requests.post(recommend_document, json={
        "user_id" : int(user_id),
        "label": label,
        "response_time": str(response_time),
        "document_id" : document_id
        }).json()

        # print(posts)
    

        next = posts["document_id"]
        predictions.append(label.lower())
        # print(posts["prediction"])
        # print(posts.keys())
        
        
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

        # pred = response["prediction"].strip("start").strip(',').split(',')
        pred=response['prediction'].strip(",").split(",")
        print(pred)
        save_time(session["name"], "document labelled")
        return redirect(url_for("non_active_label", response=response, words=words, document_id=posts["document_id"], name=name, predictions=labels, pred=response["prediction"], total=total, docs_len=docs_len, elapsed_time=str(elapsed_time)[:7], secs = secs, skips=skips))

    # pred = response["prediction"].strip("start").strip(',').split(',')
    pred = response["prediction"].strip(",").split(',')
    print(pred)


    return render_template("nonactivelabel.html", response=response, words=words, document_id=document_id, text=text, name=name, predictions=labels, pred=pred, total=total, docs_len=docs_len, elapsed_time=str(elapsed_time)[:7], secs = secs, skips=skips)






@app.route("/non_active/<name>/<topic_id>//<documents>//<keywords>")
def topic(name, topic_id, documents, keywords): 
    """
    Handles displaying all documents for a specific topic in the Flask application.

    Parameters:
    - name (str): The name of the user, extracted from the URL.
    - topic_id (str): The ID of the topic, extracted from the URL.
    - documents (str): List of document IDs for the topic, extracted from the URL.
    - keywords (str): List of keywords for the topic, extracted from the URL.

    Returns:
    - If the user is not logged in (name not in session), redirects to the login page ('/login').
    - Retrieves information about the specified documents and keywords for the topic.
    - Calculates and displays the documents, topic ID, keywords, and elapsed time for the topic page.

    Routes:
    - GET: '/non_active/<name>/<topic_id>/<documents>/<keywords>'

    Method:
    - GET
    """
    # print(topic_id)
    # res = get_single_document(documents, all_texts)
    keywords = keywords.strip("'[]'").split("', '")
    docs = list(set(session["labelled_document"].strip(",").split(",")))
    docs_len = len(docs)
    elapsed_time = datetime.now() - session["begin"]
    res = get_single_document(documents.strip("'[]'").split(", "), all_texts, docs=docs)
    secs = round(elapsed_time.total_seconds())
    save_time(session["name"], "viewing all documents for topic " + str(topic_id))
    return  render_template("topic.html", res = res, topic_id=topic_id, docs_len = docs_len, keywords=keywords, elapsed_time=str(elapsed_time), secs=secs) 
 
 

@app.route("/<name>/labeled/<document_id>")

def view_labeled(name,document_id):
    """
    Handles displaying labeled information for a specific document in the Flask application.

    Parameters:
    - name (str): The name of the user, extracted from the URL.
    - document_id (str): The ID of the document, extracted from the URL.

    Returns:
    - If the user is not logged in (name not in session), redirects to the login page ('/login').
    - Retrieves labeled information for the specified document.
    - Calculates and displays the document text, labeled response, document ID, and elapsed time for the view labeled page.

    Routes:
    - GET: '/<name>/labeled/<document_id>'

    Method:
    - GET
    """
    text = all_texts["text"][document_id]
    response = extract_label(name, document_id )
    elapsed_time = datetime.now() - session["begin"]
    secs = round(elapsed_time.total_seconds())
    save_time(session["name"], "relabelling document")
    save_time(session["name"], str(document_id))
    return render_template("viewlabeled.html", text=text, response=response, document_id=document_id, elapsed_time=str(elapsed_time), secs=secs) 



@app.route("/<name>/labeled_list/")
def labeled_list(name):
    """
    Handles displaying a list of labeled documents for a user in the Flask application.

    Parameters:
    - name (str): The name of the user, extracted from the URL.

    Returns:
    - If the user is not logged in (name not in session), redirects to the login page ('/login').
    - Retrieves labeled documents and completed documents for the user.
    - Calculates and displays the list of labeled documents, completed documents, elapsed time, and number of documents for the labeled list page.

    Routes:
    - GET: '/<name>/labeled_list/'

    Method:
    - GET
    """
    labe = session["labelled_document"]
    docs = list(set(session["labelled_document"].strip(",").split(",")))
    docs_len = len(docs)
    docss = labelled_docs(labe, all_texts)
    completed = completed_json_(name)
    completed_docs = get_completed(completed, all_texts)
    elapsed_time = datetime.now() - session["begin"]
    secs = round(elapsed_time.total_seconds())
    save_time(session["name"], "viewing labelled documents")
    return render_template("completed.html", completed_docs=completed_docs, docss=docss, secs=secs, elapsed_time=str(elapsed_time), docs_len=docs_len)
 

@app.route("/<name>/edit_response/<document_id>")
def edit_labels(name, document_id):
    """
    Handles redirecting to the appropriate editing labels route based on the document's active status in the Flask application.

    Parameters:
    - name (str): The name of the user, extracted from the URL.
    - document_id (str): The ID of the document, extracted from the URL.

    Returns:
    - If the document is active, redirects to the active editing labels page.
    - If the document is non-active, redirects to the non-active editing labels page.

    Routes:
    - GET: '/<name>/edit_response/<document_id>'
    """
    save_time(session["name"], "editing labels")
    if session["is_active"] == True:
        return redirect(url_for("active", name=name, document_id=document_id))

    if session["is_active"] == False:
        return redirect(url_for("non_active_label", name=name, document_id=document_id))



    
import re, numpy as np, pandas as pd
import pickle
from xml.dom import minidom
import os


# def read_data(path):
#     return pd.read_json(path)

def read_data(path):
    """
    Read JSON data from a file. The data respresents all the documents used to train the model

    Args:
        path (str): The path to the JSON file.

    Returns:
        pandas.DataFrame: A DataFrame containing the JSON data.
    """
    return pd.read_json(path)





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

def get_words(dat, raw_string):
    """
    Extract words from specified spans in a raw string.

    This function takes a dictionary of spans and a raw string as input. It extracts
    the words covered by the specified spans in the raw string.

    Args:
        dat (dict): A dictionary containing spans for different categories or topics.
            Each category is a key in the dictionary, and the value is a dictionary
            with 'spans' key containing a list of span tuples (start, end).
        raw_string (str): The raw string from which words will be extracted.

    Returns:
        dict: A dictionary where keys represent categories or topics, and values are
            sets of words extracted from the specified spans in the raw string.
    
    Example:
        dat = {
            'category1': {'spans': [(0, 5), (10, 15)]},
            'category2': {'spans': [(5, 10), (15, 20)]}
        }
        raw_string = "This is a sample raw string."
        result = get_words(dat, raw_string)

        The result will be:
        {
            'category1': {'is', 'This'},
            'category2': {'raw', 'sample'}
        }
    """
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





# def highlight_words(text, words):
#     for word in words:
#         text = text.replace(word, f"<span style='background-color:yellow'>{word}</span>")
#     return text

def highlight_words(text, words):
    """
    Highlight specified words in a text with a yellow background.

    This function takes a text and a set of words as input and adds HTML tags to
    highlight the specified words with a yellow background color.

    Args:
        text (str): The input text in which words will be highlighted.
        words (set): A set of words to be highlighted in the text.

    Returns:
        str: The input text with specified words highlighted using HTML tags.

    Example:
        text = "This is a sample text containing some keywords."
        words = {'sample', 'keywords'}
        result = highlight_words(text, words)

        The result will be:
        "This is a <span style='background-color:yellow'>sample</span> text containing some <span style='background-color:yellow'>keywords</span>."
    """
    for word in words:
        text = text.replace(word, f"<span style='background-color:yellow'>{word}</span>")
    return text


# def save_response(name, label, response_time, document_id, user_id):
#     root = minidom.Document()
#     xml = root.createElement('root')
#     root.appendChild(xml)

#     user_name = root.createElement('name')
#     user_name.setAttribute("name", name)
#     xml.appendChild(user_name)

#     response_times = root.createElement('response_time')
#     response_times.setAttribute("response_time", str(response_time))
#     xml.appendChild(response_times)

#     document_ids = root.createElement('document_id')
#     document_ids.setAttribute("document_id", str(document_id))
#     xml.appendChild(document_ids)

#     labels = root.createElement('label')
#     labels.setAttribute("label", label)
#     xml.appendChild(labels)

#     user_ids = root.createElement('user_id')
#     user_ids.setAttribute("user_id", str(user_id))
#     xml.appendChild(user_ids)

#     xml_str = root.toprettyxml(indent ="\t")

#     directory = "./static/responses/"+name

#     save_path_file = directory + "/"+ str(document_id) +".xml"
#     try:
#         os.makedirs(directory)
#     except:
#         print("all_good")
#     with open(save_path_file, "w") as f:
#         f.write(xml_str)
#     return xml_str


def save_response(name, label, response_time, document_id, user_id):
    """
    Save annotation response to an XML file.

    This function creates an XML document to store annotation details including user name,
    response time, document ID, annotation label, and user ID. It then saves the XML document
    to a specified directory.

    Args:
        name (str): The user's name or identifier.
        label (str): The annotation label or category.
        response_time (float): The time taken to complete the annotation.
        document_id (int): The unique ID of the annotated document.
        user_id (int): The unique ID of the annotating user.

    Returns:
        str: The XML document as a string.

    Example:
        name = "user123"
        label = "important"
        response_time = 5.6
        document_id = 12345
        user_id = 9876
        result = save_response(name, label, response_time, document_id, user_id)

        This function will create an XML document with user details, save it to
        "./static/responses/user123/12345.xml", and return the XML document as a string.
    """
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

    xml_str = root.toprettyxml(indent="\t")

    directory = "./static/responses/" + name

    save_path_file = directory + "/" + str(document_id) + ".xml"
    try:
        os.makedirs(directory)
    except:
        print("all_good")
    with open(save_path_file, "w") as f:
        f.write(xml_str)
    return xml_str




# def get_texts (topic_list, all_texts, docs):
#     results = {}
#     for a in topic_list["cluster"].keys():
#         sub_results = {}
#         for b in topic_list["cluster"][a]:
#             if str(b) in docs:
#                 continue
#             sub_results[str(b)] = all_texts["text"][str(b)]
#         results[a]= sub_results
#     return results


def get_texts(topic_list, all_texts, docs):
    """
    Retrieve text data for specified topics and documents.

    Parameters:
    - topic_list (dict): A dictionary containing topics and associated document lists.
    - all_texts (dict): A dictionary containing text data where keys are document IDs and values are corresponding documents.
    - docs (set): A set of document IDs to exclude from the results.

    Returns:
    - results (dict): A dictionary containing text data for specified topics and documents.

    This function takes a 'topic_list' dictionary, which includes topics and associated document lists, a 'all_texts' dictionary containing
    document text data, and a 'docs' set representing documents to exclude. It retrieves text data for specified documents under each topic.

    The function returns 'results,' a dictionary where each key represents a topic, and the associated value is a sub-dictionary
    containing document IDs and their corresponding texts for that topic. Documents listed in the 'docs' set are excluded.
    """
    results = {}

    for topic, document_list in topic_list["cluster"].items():
        sub_results = {}

        for document_id in document_list:
            if str(document_id) in docs:
                continue

            try:
                sub_results[str(document_id)] = all_texts["text"][str(document_id)]
            except KeyError:
                # Handle the case where the document ID is not found in 'all_texts'
                continue

        results[topic] = sub_results

    return results




# def get_sliced_texts(topic_list, all_texts, docs):
#     results = {}
#     for a in topic_list["cluster"].keys():
#         sub_results = {}
#         counter = 0
#         # print(a, len(topic_list["cluster"][a]))
#         if len(topic_list["cluster"][a]) == 0:
#             continue
#         for b in topic_list["cluster"][a]:
#             if str(b) in docs:
#                 continue
#             if counter < 6:
#                 sub_results[str(b)] = all_texts["text"][str(b)]
#             counter+=1
#         if len(sub_results) != 0:   
#             results[a]= sub_results
#     return results 


def get_sliced_texts(topic_list, all_texts, docs):
    """
    Retrieve a limited number of text entries from each topic cluster.

    This function extracts a limited number of text entries from each topic cluster
    based on the specified count (up to 6 per cluster) while excluding documents in 'docs'.

    Args:
        topic_list (dict): A dictionary containing topic clusters.
        all_texts (dict): A dictionary of all available text entries.
        docs (list): A list of documents to exclude from extraction.

    Returns:
        dict: A dictionary where keys represent topic clusters, and values are sub-dictionaries
            containing the extracted text entries.

    Example:
        topic_list = {
            "cluster1": [1, 2, 3, 4, 5],
            "cluster2": [6, 7, 8, 9, 10],
            "cluster3": [11, 12, 13, 14, 15]
        }
        all_texts = {
            "text": {
                "1": "Text 1 content",
                "2": "Text 2 content",
                # ...
                "15": "Text 15 content"
            }
        }
        docs = [3, 8]

        result = get_sliced_texts(topic_list, all_texts, docs)

        The result will be a dictionary with limited text entries from each topic cluster:
        {
            "cluster1": {"1": "Text 1 content", "2": "Text 2 content"},
            "cluster2": {"6": "Text 6 content", "7": "Text 7 content", "9": "Text 9 content", "10": "Text 10 content"},
            "cluster3": {"11": "Text 11 content", "12": "Text 12 content", "13": "Text 13 content", "14": "Text 14 content", "15": "Text 15 content"}
        }
    """
    results = {}
    for a in topic_list["cluster"].keys():
        sub_results = {}
        counter = 0
        if len(topic_list["cluster"][a]) == 0:
            continue
        for b in topic_list["cluster"][a]:
            if str(b) in docs:
                continue
            if counter < 6:
                sub_results[str(b)] = all_texts["text"][str(b)]
            counter += 1
        if len(sub_results) != 0:   
            results[a] = sub_results
    return results





# def get_single_document( top, all_texts, docs):
#     results = {}
#     for a in top:
#         if str(a) in docs:
#                 continue
#         results[str(a)] = all_texts["text"][str(a)]
#     return results 

def get_single_document(topics, all_texts, existing_documents):
    """
    Retrieve single documents from a collection of texts based on specified topic indices.

    Parameters:
    - topics (list or set): A list or set of topic indices to retrieve documents for.
    - all_texts (dict): A dictionary containing text data where keys are topic indices and values are corresponding documents.
    - existing_documents (set): A set of topic indices representing documents that should be excluded from the results.

    Returns:
    - results (dict): A dictionary containing documents for the specified topics that are not in the existing documents set.
    
    This function takes a list or set of 'topics' (topic indices), a 'all_texts' dictionary containing text data, and a 'existing_documents' set.
    It iterates through the specified 'topics' and retrieves documents from the 'all_texts' dictionary for topics that are not already in the 'existing_documents' set.

    The function returns a dictionary 'results' where each key is a topic index, and the corresponding value is the document text.
    """
    results = {}
    for topic in topics:
        if str(topic) in existing_documents:
            continue
        results[str(topic)] = all_texts["text"][str(topic)]
    return results



# def save_labels(session):
#     import json
#     with open('./static/users/users.json') as user_file:
#         name_string = user_file.read()
#         names = json.loads(name_string)

#     with open('./static/users/users.json', mode='w', encoding='utf-8') as name_json:
#         names[session["name"]]["labels"] = session["labels"]
#         names[session["name"]]["labelled_document"] = session["labelled_document"]
#         json.dump(names, name_json, indent=4)


def save_labels(session):
    """
    Save user labels and labeled documents to a JSON file.

    Parameters:
    - session (dict): A dictionary containing user session data, including labels and labeled documents.

    This function reads an existing JSON file containing user data from './static/users/users.json', updates the user's labels
    and labeled document information in the dictionary, and then writes the updated data back to the same JSON file.

    The 'session' dictionary should include the following keys:
    - "name": The user's name or identifier.
    - "labels": A dictionary containing label information.
    - "labelled_document": A dictionary containing information about labeled documents.

    The function does not return any value but updates the JSON file with the modified user data.
    """
    import json

    # Read the existing user data from the JSON file
    with open('./static/users/users.json', 'r') as user_file:
        name_string = user_file.read()
        names = json.loads(name_string)

    # Update the user's labels and labeled document information
    names[session["name"]]["labels"] = session["labels"]
    names[session["name"]]["labelled_document"] = session["labelled_document"]

    # Write the updated user data back to the JSON file
    with open('./static/users/users.json', mode='w', encoding='utf-8') as name_json:
        json.dump(names, name_json, indent=4)






# def save_time(session, current_time):
#     import json
#     with open('.\\static\\users\\users.json') as user_file:
#         name_string = user_file.read()
#         names = json.loads(name_string)



# def labelled_docs(labe, all_texts):
#     results = {}
#     labelled = [x for x in labe.strip(",").split(",")][: : -1]
#     for a in labelled:
#         try:
#             results[a] = all_texts["text"][a]
#         except:
#             continue
#     return results


def labelled_docs(labels, all_texts):
    """
    Retrieve labeled documents based on a list of document labels.

    Parameters:
    - labels (str): A comma-separated string of document labels.
    - all_texts (dict): A dictionary containing text data where keys are document labels and values are corresponding documents.

    Returns:
    - results (dict): A dictionary containing documents for the specified labels.

    This function takes a comma-separated string of 'labels' (document labels), splits it into individual labels, and retrieves
    documents from the 'all_texts' dictionary based on these labels.

    The function returns a dictionary 'results' where each key is a document label, and the corresponding value is the document text.
    If a label is not found in 'all_texts', it is skipped.
    """
    results = {}
    
    # Split the comma-separated labels, reverse the order, and iterate through them
    labelled = [x for x in labels.strip(",").split(",")][::-1]
    for label in labelled:
        try:
            results[label] = all_texts["text"][label]
        except KeyError:
            continue
    
    return results




# def extract_label (name, number):
#     responses_path =("./static/responses/" + name + "/" + number +".xml" )
#     doc = minidom.parse(responses_path)
#     root = doc.getElementsByTagName("label")
#     label = None
#     for a in root:
#         label = a.getAttribute("label")
#     return label

def extract_label(name, number):
    """
    Extract a label attribute from an XML file.

    Parameters:
    - name (str): The name or identifier of the file's owner.
    - number (str): The number or identifier of the XML file.

    Returns:
    - label (str or None): The value of the "label" attribute from the XML file, or None if not found.

    This function constructs the path to an XML file based on the 'name' and 'number' provided, parses the XML file,
    and retrieves the "label" attribute value from the XML's root element.

    If the "label" attribute is found, its value is returned as a string. If the attribute is not found, the function
    returns None.
    """
    import xml.dom.minidom as minidom

    # Construct the path to the XML file
    responses_path = ("./static/responses/" + name + "/" + number + ".xml")

    # Initialize the label variable as None
    label = None

    try:
        # Parse the XML file
        doc = minidom.parse(responses_path)

        # Get the root element
        root = doc.getElementsByTagName("label")

        # Iterate through the root elements and extract the "label" attribute value
        for elem in root:
            label = elem.getAttribute("label")

    except Exception as e:
        # Handle any exceptions, such as file not found or parsing errors
        print(f"Error extracting label from {responses_path}: {e}")
        label = None

    return label


# def completed_json_ (name):
#     import pandas as pd
#     import glob
#     path = "./static/responses/" + name+"/*.xml"
#     doc_id = []
#     doc_label = []
#     res = []
#     for a in glob.glob(path):
#         doc = minidom.parse(a)
#         user_label = doc.getElementsByTagName("label")
#         document_id = doc.getElementsByTagName("document_id")
#         for a in document_id:
#             doc = a.getAttribute("document_id")
#             doc_id.append(doc)
#         for b in user_label:
#             label = b.getAttribute("label")
#             doc_label.append(label)
#     for c in zip(doc_id, doc_label):
#         res.append(c)
#     df = pd.DataFrame(res, columns=["document_id", "label"])
#     completed_json = {}
#     for a in set(df["label"]):
#         completed_json[a]=list(df[df["label"]==a]["document_id"])
#     return completed_json


def completed_json_(name):
    """
    Create a completed JSON representation of document labels for a given user.

    Parameters:
    - name (str): The name or identifier of the user whose labeled documents are being processed.

    Returns:
    - completed_json (dict): A JSON-like dictionary representing labeled documents grouped by labels.

    This function processes XML files in a specified directory based on the 'name' provided. It extracts document IDs and labels
    from these XML files and organizes them into a dictionary where labels are keys and associated document IDs are stored in lists.

    The function returns 'completed_json,' a dictionary where each key represents a label, and the associated value is a list of
    document IDs labeled with that label.
    """
    import pandas as pd
    import glob
    import xml.dom.minidom as minidom

    # Construct the path to the XML files
    path = "./static/responses/" + name + "/*.xml"

    doc_id = []
    doc_label = []

    # Iterate through XML files in the specified directory
    for file_path in glob.glob(path):
        doc = minidom.parse(file_path)
        user_label = doc.getElementsByTagName("label")
        document_id = doc.getElementsByTagName("document_id")

        # Extract document IDs and labels from each XML file
        for elem in document_id:
            doc_id.append(elem.getAttribute("document_id"))

        for elem in user_label:
            doc_label.append(elem.getAttribute("label"))

    # Create a DataFrame to organize the extracted data
    res = list(zip(doc_id, doc_label))
    df = pd.DataFrame(res, columns=["document_id", "label"])

    # Initialize the completed JSON dictionary
    completed_json = {}

    # Group document IDs by labels in the DataFrame
    for label in set(df["label"]):
        completed_json[label] = list(df[df["label"] == label]["document_id"])

    return completed_json







# def get_completed(completed_json, all_texts):
#     results = {}
#     for a in completed_json.keys():
#         sub_results = {}
#         for b in completed_json[a]:
#             sub_results[str(b)] = all_texts["text"][str(b)]
#             results[a]= sub_results
            
#     return results


def get_completed(completed_json, all_texts):
    """
    Retrieve completed documents based on a completed JSON representation.

    Parameters:
    - completed_json (dict): A JSON-like dictionary representing labeled documents grouped by labels.
    - all_texts (dict): A dictionary containing text data where keys are document IDs and values are corresponding documents.

    Returns:
    - results (dict): A dictionary containing completed documents grouped by labels.

    This function takes a 'completed_json' dictionary, which represents labeled documents grouped by labels, and a 'all_texts' dictionary
    containing document text data. It retrieves the document texts for the specified document IDs in 'completed_json' and organizes them
    into a dictionary where labels are keys, and the associated documents are stored in sub-dictionaries.

    The function returns 'results,' a dictionary where each key represents a label, and the associated value is a sub-dictionary
    containing document IDs and their corresponding texts for that label.
    """
    results = {}

    for label, document_ids in completed_json.items():
        sub_results = {}

        for document_id in document_ids:
            try:
                sub_results[str(document_id)] = all_texts["text"][str(document_id)]
            except KeyError:
                # Handle the case where the document ID is not found in 'all_texts'
                continue

        results[label] = sub_results

    return results




# def get_recommended_topic(recommended, topics, all_texts):
#     results = {}
#     for a in topics["cluster"].keys():
#         sub_results = {}
#         for b in topics["cluster"][a]:
#             if b == recommended:
#                 for c in topics["cluster"][a]:
#                     sub_results[str(c)] = all_texts["text"][str(c)]
#                 results[a] = sub_results
#                 recommended_topic = a
#     return recommended_topic,  results


def get_recommended_topic(recommended, topics, all_texts):
    """
    Retrieve recommended topic and associated documents from a topic-clustered dataset.

    Parameters:
    - recommended (str): The recommended topic to retrieve.
    - topics (dict): A dictionary containing clustered topics and associated document lists.
    - all_texts (dict): A dictionary containing text data where keys are document IDs and values are corresponding documents.

    Returns:
    - recommended_topic (str): The recommended topic.
    - results (dict): A dictionary containing text data for documents associated with the recommended topic.

    This function takes a 'recommended' topic, a 'topics' dictionary that includes clustered topics and associated document lists,
    and a 'all_texts' dictionary containing document text data. It retrieves text data for documents associated with the specified
    recommended topic.

    The function returns 'recommended_topic,' the name of the recommended topic, and 'results,' a dictionary where each key represents
    a cluster within the recommended topic, and the associated value is a sub-dictionary containing document IDs and their corresponding texts.
    """
    results = {}

    for cluster_name, document_list in topics["cluster"].items():
        sub_results = {}

        if recommended in document_list:
            for document_id in document_list:
                try:
                    sub_results[str(document_id)] = all_texts["text"][str(document_id)]
                except KeyError:
                    # Handle the case where the document ID is not found in 'all_texts'
                    continue

            results[cluster_name] = sub_results
            recommended_topic = cluster_name

    return recommended_topic, results



# def save_time(name, page):
#     from csv import writer
#     import datetime
#     with open ("./static/responses/"+name+"/time.csv", 'a', newline='') as f_object:
#         writer_object = writer(f_object)
#         writer_object.writerow([page, datetime.datetime.now()])
#         f_object.close()


def save_time(name, page):
    """
    Save the timestamp when a user accesses a specific page to a CSV file.

    Parameters:
    - name (str): The name or identifier of the user.
    - page (str): The name or identifier of the page the user accessed.

    This function appends a new row to a CSV file located in the './static/responses/<name>/time.csv' directory.
    The row contains two columns: 'page' (the accessed page) and 'timestamp' (the current date and time).

    It is used to record when a user accesses different pages and stores the timestamp for future reference.
    """
    from csv import writer
    import datetime

    # Construct the path to the CSV file
    file_path = "./static/responses/" + name + "/time.csv"

    # Get the current date and time
    current_timestamp = datetime.datetime.now()

    # Open the CSV file in append mode and write the data
    with open(file_path, 'a', newline='') as f_object:
        writer_object = writer(f_object)
        writer_object.writerow([page, current_timestamp])

    # Close the file after writing
    f_object.close()



# def change_permissions_recursive(path, mode):
#     import os
#     for root, dirs, files in os.walk(path, topdown=False):
#         for dir in [os.path.join(root,d) for d in dirs]:
#             os.chmod(dir, mode)
#     for file in [os.path.join(root, f) for f in files]:
#             os.chmod(file, mode)


def change_permissions_recursive(path, mode):
    """
    Recursively change permissions (mode) for files and directories under the specified path.

    Parameters:
    - path (str): The root directory path from which to start recursively changing permissions.
    - mode (int): The permission mode to apply (e.g., 0o755 for read, write, and execute for owner, and read and execute for others).

    This function traverses the directory structure starting from the 'path' provided and applies the specified 'mode' to both
    directories and files found within that directory and its subdirectories.

    Note: Be cautious when changing permissions recursively, as it can have a significant impact on system security.
    """
    import os

    # Recursively traverse the directory structure from the bottom up
    for root, dirs, files in os.walk(path, topdown=False):
        for directory in [os.path.join(root, d) for d in dirs]:
            # Change permissions for directories
            os.chmod(directory, mode)

        for file_path in [os.path.join(root, f) for f in files]:
            # Change permissions for files
            os.chmod(file_path, mode)




# def save_first_time(name, page):
#     from csv import writer
#     import datetime
#     change_permissions_recursive('./static/responses', 0o777)
#     with open ("./static/responses/"+name+"/time.csv", 'w', newline='') as f_object:
#         writer_object = writer(f_object)
#         writer_object.writerow([page, datetime.datetime.now()])
#         f_object.close()


def save_first_time(name, page):
    """
    Save the timestamp when a user first accesses a specific page to a CSV file with changed permissions.

    Parameters:
    - name (str): The name or identifier of the user.
    - page (str): The name or identifier of the page the user first accessed.

    This function first recursively changes the permissions of the 'responses' directory and its contents to '0o777'
    (read, write, and execute for everyone) and then appends a new row to a CSV file located in the './static/responses/<name>/time.csv' directory.
    The row contains two columns: 'page' (the accessed page) and 'timestamp' (the current date and time).

    It is used to record when a user first accesses different pages with changed directory permissions to ensure that the user can write to the CSV file.
    """
    from csv import writer
    import datetime

    # Change permissions recursively for the 'responses' directory
    change_permissions_recursive('./static/responses', 0o777)

    # Construct the path to the CSV file
    file_path = "./static/responses/" + name + "/time.csv"

    # Get the current date and time
    current_timestamp = datetime.datetime.now()

    # Open the CSV file in write mode (creates a new file if it doesn't exist) and write the data
    with open(file_path, 'w', newline='') as f_object:
        writer_object = writer(f_object)
        writer_object.writerow([page, current_timestamp])

    # Close the file after writing
    f_object.close()




# def make_folder(name):
#     import os
#     parent_dir= "./static/responses/"
#     mode = 0o666
#     path = os.path.join(parent_dir, name)
#     os.mkdir(path, mode)


def make_folder(name):
    """
    Create a new directory under './static/responses/' with the specified 'name'.

    Parameters:
    - name (str): The name or identifier of the directory to be created.

    This function creates a new directory with the provided 'name' under the './static/responses/' directory.
    The 'mode' parameter specifies the permission mode for the newly created directory.
    """
    import os

    # Specify the parent directory where the new directory will be created
    parent_dir = "./static/responses/"

    # Define the permission mode for the new directory (0o666 grants read and write permissions for everyone)
    mode = 0o666

    # Create the full path to the new directory by joining the parent directory and the provided 'name'
    path = os.path.join(parent_dir, name)

    # Create the new directory with the specified 'name' and 'mode'
    os.mkdir(path, mode)

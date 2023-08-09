import numpy as np
from sklearn import metrics


# Calculates purity between two sets of labels
def purity_score(y_true, y_pred):
    # compute contingency matrix (also called confusion matrix)
    contingency_matrix = metrics.cluster.contingency_matrix(y_true, y_pred)
    print(contingency_matrix)
    # return purity
    return np.sum(np.amax(contingency_matrix, axis=0)) / np.sum(contingency_matrix)

# Given topics with documents with U, pick a topic with maximum medium U
def pick_topic(topic_U):
    max_medium_topic = float('-Inf')
    max_medium_topic_probability = float('-Inf')
    for k, v in topic_U.items():
        curr_median = np.median(v)
        # print('topic {} median {}'.format(k, curr_median))
        if curr_median >= max_medium_topic_probability:
            max_medium_topic = k
            max_medium_topic_probability = curr_median

    print('max topic index is ', max_medium_topic)
    return max_medium_topic

# Find the document with maximum median U
def find_doc_for_TA(document_probas, entropy):
    doc_info_with_id = {}
    doc_info_no_id = {}
    for k, v in document_probas.items():
        lst = [(doc_id, prob*entropy[doc_id]) for doc_id, prob in v]
        lst1 = [prob*entropy[doc_id] for doc_id, prob in v] 
        doc_info_with_id[k] = lst
        doc_info_no_id[k] = lst1

    # Find the topic with maximum median U
    max_medium_topic = pick_topic(doc_info_no_id)
    # Find the most confusing document within that topic
    max_idx = np.argmax(doc_info_no_id[max_medium_topic])
    chosen_doc_id = doc_info_with_id[max_medium_topic][max_idx][0]

    return chosen_doc_id, max_medium_topic, max_idx


def remove_value_from_dict_values(dictionary, value_to_remove):
    for key, values in dictionary.items():
        if value_to_remove in values:
            values.remove(value_to_remove)


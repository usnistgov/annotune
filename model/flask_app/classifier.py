from sklearn.linear_model import SGDClassifier
from .utils.tools import purity_score
from .utils.tools import find_doc_for_TA
from .utils.tools import remove_value_from_dict_values
from sklearn.metrics.cluster import normalized_mutual_info_score
from sklearn.metrics.cluster import rand_score
from scipy.sparse import vstack
import numpy as np
from sklearn.metrics import accuracy_score
import random


'''
whether we use the test dataset for evaluation or not
'''
use_test_data = False
# This variable means if you create a global classifier, then you predeciding there
# are 20 topics in the classifier. Then test the accuracy of the global classifier
# on both the training and the testing dataset
# log_test_data = False


# Active Learning
class Active_Learning():
    def __init__(self, documents, doc_prob, doc_topic_prob, df, running_type, text_vectorizer, train_len, mode, test_dataset_frame):
        """
        Documents: the text corpus
        Doc_prob: a dictionary contains all the topics. Each topic 
        contains a list of documents along with their probabilities 
        belong to a specific topic
        [topic 1]: [(document a, prob 1), (document b, prob 2)...]
        """
        # self.classes = list(range(num_topics))
        # print('mode is {}'.format(mode))
        self.mode = mode
        self.docs = documents
        self.num_docs_labeled = 0
        self.last_recommended_topic = None
        self.last_recommended_doc_id = None
        self.recommended_doc_ids = set()
        self.text_vectorizer = text_vectorizer
        self.total_length = train_len + len(test_dataset_frame.text.values.tolist())

        self.train_length = train_len
        self.id_vectorizer_map = {}
        '''
        stores the scores of the documents after the user updates the classifier
        '''
        self.scores = []

        # if log_test_data:
        #     self.test_texts = text_vectorizer[train_len:train_len+100]

        '''
        user_labels: labels the user creates for documents the user views
        curr_label_num: topic numbers computed by LDA
        '''
        self.user_labels = dict()

        '''
        Parameters or regressor can be changed later
        '''
        self.classifier = self.initialize_classifier(running_type)
        self.test_texts = test_dataset_frame.text.values.tolist()
        self.test_general_labels = test_dataset_frame.label.values.tolist()
        self.test_sub_labels = test_dataset_frame.sub_labels.values.tolist()

        # Stores and track labeled documents and labels
        self.documents_track = None
        self.labels_track = []
        self.general_labels_track = []

        
        self.df = df
        self.general_labels = df['label'].tolist()
        self.specific_labels = df['sub_labels'].tolist()
        self.classes = []
        # self.classes = np.unique(self.specific_labels)
        
        '''
        Mode 1 mean using topic modeling. Otherwise, just use active learning
        '''
        if self.mode == 1:
            self.doc_topic_prob = np.array(doc_topic_prob)
            # self.sorted_doc_topic_prob = np.sort(self.doc_topic_prob, axis=1)[:, ::-1]
            self.doc_probs = doc_prob
    
    def update_doc_probs(self, doc_prob, doc_topic_prob):            
        self.doc_topic_prob = np.array(doc_topic_prob)
        # self.sorted_doc_topic_prob = np.sort(self.doc_topic_prob, axis=1)[:, ::-1]
        self.doc_probs = doc_prob

    def initialize_classifier(self, classifier_type: str):
        classifier_type = classifier_type.lower()

        if classifier_type == 'logreg':
            return SGDClassifier(loss="log_loss", penalty="l2", max_iter=1000, tol=1e-3, random_state=42, learning_rate="adaptive", eta0=0.1, validation_fraction=0.2)
        elif classifier_type == 'logreg_modal':
            print('Implement other types')
            return None
        else:
            print('Implement other types')
            return None

     
    def update_median_prob(self, topic_num, idx_in_topic):
        try:
            self.doc_probs[topic_num].pop(idx_in_topic)
        except:
            self.doc_probs.pop(topic_num)
        

    '''
    Preference function can be changed or chosen for NAITM
    '''
    def preference(self, update):
        if not update and self.last_recommended_doc_id is not None:
            # print('return last recommended id')
            if self.last_recommended_doc_id in self.scores:
                return self.last_recommended_doc_id, self.scores[self.last_recommended_doc_id]
            return self.last_recommended_doc_id, -1
        
        if self.mode == 1:
            if len(self.classes) < 2:
                chosen_idx = random.randint(0, self.train_length)

                while chosen_idx in self.recommended_doc_ids:
                    try:
                        chosen_idx = random.randint(0, self.train_length)
                    except Exception as e: 
                        print(e)


                self.recommended_doc_ids.add(chosen_idx)
                self.last_recommended_doc_id = chosen_idx

                print('picked doc is ', chosen_idx)


                return chosen_idx, -1
            else:
                try:
                    for ele in self.recommended_doc_ids:
                        self.scores[ele] = float('-Inf')

                    chosen_idx, chosen_topic, chosen_idx_in_topic = find_doc_for_TA(self.doc_probs, self.scores)
                    self.update_median_prob(chosen_topic, chosen_idx_in_topic)
                    
                    while chosen_idx in self.recommended_doc_ids:
                        print('Selected Documents still exists')
                        chosen_idx, chosen_topic, chosen_idx_in_topic = find_doc_for_TA(self.doc_probs, self.scores)
                        self.update_median_prob(chosen_topic, chosen_idx_in_topic)

                    print('max median topic is ', chosen_topic)

                    self.last_recommended_topic = chosen_topic
                    self.recommended_doc_ids.add(chosen_idx)
                    self.last_recommended_doc_id = chosen_idx
                    

                    return chosen_idx, self.scores[chosen_idx]
                except:
                    return None, -1
        else:
            if len(self.classes) < 2:
                chosen_idx = random.randint(0, self.train_length)

                while chosen_idx in self.recommended_doc_ids:
                    try:
                        chosen_idx = random.randint(0, self.train_length)
                    except Exception as e: 
                        print(e)


                self.recommended_doc_ids.add(chosen_idx)
                self.last_recommended_doc_id = chosen_idx
                return chosen_idx, -1
            else:

                for ele in self.recommended_doc_ids:
                    self.scores[ele] = float('-Inf')

                chosen_idx = np.argmax(self.scores)
                

                '''
                Don't show the users an already shown document
                '''
                while chosen_idx in self.recommended_doc_ids:
                    print('Selected Documents still exists')
                    self.scores[chosen_idx] = float('-Inf')
                    try:
                        chosen_idx = np.argmax(self.scores)
                    except Exception as e: 
                        print(e)
                

                print('Classifier in progess...')
                print('\033[1mScore of the current document is {}\033[0m'.format(self.scores[chosen_idx]))
                self.recommended_doc_ids.add(chosen_idx)
                self.last_recommended_doc_id = chosen_idx
                return chosen_idx, self.scores[chosen_idx]


    def recommend_document(self, update):
        document_id, score = self.preference(update)

        print(self.classes)
        return document_id, score

    def fit_classifier(self, initialized= False):
        if initialized:
            for i in range(len(self.labels_track)):
                self.classifier.partial_fit(self.documents_track, self.labels_track, self.classes)
        else:
            self.classifier.partial_fit(self.documents_track, self.labels_track, self.classes)

        self.update_classifier()

    def is_labeled(self, doc_id):
        return doc_id in self.user_labels

    def update_classifier(self):
        guess_label_probas = self.classifier.predict_proba(self.text_vectorizer[0:self.train_length])
        guess_label_logprobas = self.classifier.predict_log_proba(self.text_vectorizer[0:self.train_length])
        scores = -np.sum(guess_label_probas*guess_label_logprobas, axis = 1)
        self.scores = scores
        
    def label(self, doc_id, user_label):
        # if self.mode == 1:
        if True:
            if int(doc_id) != self.last_recommended_doc_id and self.mode != 0:
                self.recommended_doc_ids.add(int(doc_id))
                remove_value_from_dict_values(self.doc_probs, int(doc_id))
            
            
            if self.is_labeled(doc_id):
                # if user_label in self.user_label_number_map:
                if user_label in self.classes:
                    # label_num = self.user_label_number_map[user_label]
                    self.user_labels[doc_id] = user_label
                    self.labels_track[self.id_vectorizer_map[doc_id]] = user_label
                    if len(self.classes) >= 2:
                        self.fit_classifier()
                        
                else:
                    self.user_labels[doc_id] = user_label
                    self.classes.append(user_label)
                    self.labels_track[self.id_vectorizer_map[doc_id]] = user_label
                    if len(self.classes) >= 2:
                        self.classifier = self.initialize_classifier('logreg')

                        self.fit_classifier(initialized=True)
                        

            elif user_label in self.classes:  
                self.user_labels[doc_id] = user_label
                self.id_vectorizer_map[doc_id] = self.num_docs_labeled
                # print(self.id_vectorizer_map)
                '''
                Adding documents and labels and track them
                '''
                self.labels_track.append(user_label)
                self.general_labels_track.append(self.general_labels[doc_id])
                
                if self.documents_track is None:
                    self.documents_track = self.text_vectorizer[doc_id]
                else:
                    self.documents_track = vstack((self.documents_track, self.text_vectorizer[doc_id]))
                
                if len(self.classes) >=  2:
                    self.fit_classifier()
                        

                self.num_docs_labeled += 1

                print('\033[1mnum docs labeled {}\033[0m'.format(self.num_docs_labeled))
            else:
                self.classes.append(user_label)
                self.id_vectorizer_map[doc_id] = self.num_docs_labeled
                # self.user_label_number_map[user_label] = user_label
                # self.reverse_user_label_number_map[label_num] = user_label
                # self.curr_label_num.append(label_num)
                self.user_labels[doc_id] = user_label

                self.labels_track.append(user_label)
                self.general_labels_track.append(self.general_labels[doc_id])
                if self.documents_track is None:
                    self.documents_track = self.text_vectorizer[doc_id]
                else:
                    self.documents_track = vstack((self.documents_track, self.text_vectorizer[doc_id]))

                if len(self.classes) >= 2:
                    self.classifier = self.initialize_classifier('logreg')
                    self.fit_classifier(initialized=True)
                    
    
                self.num_docs_labeled += 1
        
    
    def predict_label(self, doc_id):       
        # print('labels track {}'.format(self.labels_track))
        doc_id = int(doc_id)
        # print('user_label_number_map is {}'.format(self.user_label_number_map))
        if len(self.classes) >= 2:
            classes = self.classifier.classes_
            probabilities = self.classifier.predict_proba(self.text_vectorizer[doc_id])[0]
            sorted_indices = probabilities.argsort()[::-1]
            top_three_indices = sorted_indices[:3]
            

            
            result = []
            for ele in top_three_indices:
                # result += classes[ele] + '    Confidence: ' + str(round(probabilities[ele], 2)) + '\n'
                result.append(classes[ele])

            # print('id_vectorizer_map is {}'.format(self.id_vectorizer_map))
            print('prediction result is {}'.format(result))

            classes = np.array(classes)
            dropdown_indices = classes[sorted_indices]
            
            return result, dropdown_indices
        else:
            return ["Model suggestion starts after two distinct labels are created two labels to start active learning"], []
        
    def eval_classifier(self):
        local_training_preds = self.classifier.predict(self.text_vectorizer)
        local_training_acc = accuracy_score(self.specific_labels[0:self.train_length], local_training_preds[0:self.train_length])

        
        if use_test_data == True:
            local_testing_acc = accuracy_score(self.test_sub_labels, local_training_preds[self.train_length:self.total_length])
            test_purity = purity_score(self.test_general_labels, local_training_preds[self.train_length:self.total_length])
            test_RI = rand_score(self.test_general_labels, local_training_preds[self.train_length:self.total_length])
            test_NMI = normalized_mutual_info_score(self.test_general_labels, local_training_preds[self.train_length:self.total_length])
        else:
            # print('setting test results to -1')
            local_testing_acc = -1
            test_purity = -1
            test_RI = -1
            test_NMI = -1
        
        classifier_purity = purity_score(self.general_labels[0:self.train_length], local_training_preds[0:self.train_length])
        classifier_RI = rand_score(self.general_labels[0:self.train_length], local_training_preds[0:self.train_length])
        classifier_NMI = normalized_mutual_info_score(self.general_labels[0:self.train_length], local_training_preds[0:self.train_length])

        
        

        print('train acc {}; purity {}; RI {}; NMI {}'.format(local_training_acc, classifier_purity, classifier_RI, classifier_NMI))
        print('test acc {}; purity {}; RI {}; NMI {}'.format(local_testing_acc, test_purity, test_RI, test_NMI))
        return local_training_acc, local_testing_acc, classifier_purity, classifier_RI, classifier_NMI, test_purity, test_RI, test_NMI
    
    def update_text_vectorizer(self, new_text_vectorizer):
        self.text_vectorizer = new_text_vectorizer
        labeld_doc_indices = list(self.user_labels.keys())

        self.documents_track = None

        for doc_id in labeld_doc_indices:
            if self.documents_track is None:
                self.documents_track = self.text_vectorizer[doc_id]
            else:
                self.documents_track = vstack((self.documents_track, self.text_vectorizer[doc_id]))

        self.classifier = self.initialize_classifier('logreg')

        self.fit_classifier(initialized=True)
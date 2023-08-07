import random
from sklearn.linear_model import SGDClassifier
from scipy.sparse import vstack
import numpy as np
from sklearn.metrics import accuracy_score


# This var means if True, when labeling the same doc, the next recommend doc would 
# be the same
switch_doc = True

# This variable means if you create a global classifier, then you predeciding there
# are 20 topics in the classifier. Then test the accuracy of the global classifier
# on both the training and the testing dataset
global_classifier = False
global_testing = False
use_min = False


#NATM stands for neural interactive active topic modeling
class NAITM():
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
        self.classes = []
        self.docs = documents
        self.num_docs_labeled = 0
        self.last_recommended_topic = None
        self.recommended_doc_ids = set()
        self.text_vectorizer = text_vectorizer[0:train_len]
        
        self.train_length = train_len
        self.id_vectorizer_map = {}
        '''
        stores the scores of the documents after the user updates the classifier
        '''
        self.scores = []


        '''
        user_labels: labels the user creates for documents the user views
        curr_label_num: topic numbers computed by LDA
        '''
        self.user_labels = dict()

        '''
        Parameters or regressor can be changed later
        '''
        self.classifier = self.initialize_classifier(running_type)
        if global_classifier:
            unique_labels = np.unique(df.label.values.tolist())
            self.global_classifier = self.initialize_classifier(running_type)
            self.global_classes = unique_labels
            if global_testing:
                self.test_texts = text_vectorizer[train_len:train_len+100]
                self.test_labels = test_dataset_frame.label.values.tolist()[train_len:train_len+100]
            

        # Stores and track labeled documents and labels
        self.documents_track = None
        self.labels_track = []

        self.simulate_user_data = dict()
        # self.user_label_number_map = {}
        # self.reverse_user_label_number_map = {}
        self.df = df

        '''
        Mode 1 mean using topic modeling. Otherwise, just use active learning
        '''
        if self.mode == 1:
            self.doc_topic_prob = np.array(doc_topic_prob)
            self.doc_probs = doc_prob
            '''
            get the median robability of every topic
            '''
            self.median_pro = dict()
            self.cal_median_topics()
            # self.curr_label_num = list(doc_prob.keys())

            self.existing_labels = df['label'].tolist()
        

    def update_doc_probs(self, doc_prob, doc_topic_prob):            
        self.doc_topic_prob = np.array(doc_topic_prob)
        self.doc_probs = doc_prob

    def initialize_classifier(self, classifier_type: str):
        classifier_type = classifier_type.lower()

        if classifier_type == 'logreg':
            return SGDClassifier(loss="log", penalty="l2", max_iter=1000, tol=1e-3, random_state=42, learning_rate="adaptive", eta0=0.1, validation_fraction=0.2)
        elif classifier_type == 'logreg_modal':
            print('Implement other types')
            return None
        else:
            print('Implement other types')
            return None

    def cal_median_topics(self):
        for k, v in self.doc_probs.items():
            self.median_pro[k] = self.get_median_pro(v)

    def get_median_pro(self, lst):
        n = len(lst)

        if n % 2 == 0:
            return (lst[n//2][1] + lst[n//2-1][1]) / 2
        else:
            return lst[n//2][1]
     
    def update_median_prob(self, topic_num):
        try:
            # print('Poping the first document...')
            # self.median_pro[topic_num].pop(0)
            self.doc_probs[topic_num].pop(0)
            self.cal_median_topics()
        except:
            pass
        

    '''
    Preference function can be changed or chosen for NAITM
    '''
    def preference(self):
        if self.mode == 1:
            if len(self.classes) < 2:
                # print('-----------')
                # print('classes smaller than 2')
                # print('-----------')
                # print('median pro is {}'.format(self.median_pro))
                

                probs = list(self.median_pro.values())

                max_topic_idx = probs.index(max(probs))
                
                # if self.last_recommended_topic == max_topic_idx:
                #     # probs.pop(max_topic_idx)
                #     probs[max_topic_idx] = -1
                #     max_topic_idx = probs.index(max(probs))
                # print('starting while loop')
                
                i = 0
                # while self.doc_probs[max_topic_idx][0][0] in self.recommended_doc_ids and i < len(self.classes):
                while self.doc_probs[max_topic_idx][0][0] in self.recommended_doc_ids and i < self.train_length: 
                    probs[max_topic_idx] = -1
                    max_topic_idx = probs.index(max(probs))
                    i += 1

                # print('finish while loop')

                self.last_recommended_topic = max_topic_idx

                '''
                return the document id and its probability belong to the topic
                '''

                # print('current topic id is {}'.format(max_topic_idx))
                self.recommended_doc_ids.add(self.doc_probs[max_topic_idx][0][0])

                print('all recommended ids')
                print(self.recommended_doc_ids)
                return self.doc_probs[max_topic_idx][0][0], -1
            else:
                if use_min:
                    chosen_idx = np.argmin(self.scores)
                else:
                    chosen_idx = np.argmax(self.scores)

                '''
                Don't show the users an already shown document
                '''

                # print('length of recommended id is {}'.format(len(self.recommended_doc_ids)))
                while chosen_idx in self.recommended_doc_ids:
                    if use_min:
                        self.scores[chosen_idx] = float('inf')
                    else:
                        self.scores[chosen_idx] = -1
                    try:
                        if use_min:
                            chosen_idx = np.argmin(self.scores)
                        else:
                            chosen_idx = np.argmax(self.scores)
                    except:
                        print('current len of the score list is {}'.format(len(self.scores)))
                        return None
                

                print('Classifier in progess...')
                print('\033[1mScore of the current document is {}\033[0m'.format(self.scores[chosen_idx]))
                self.recommended_doc_ids.add(chosen_idx)
                return chosen_idx, self.scores[chosen_idx]
        else:
            if len(self.classes) < 2:
                # print('-----------')
                # print('num classes smaller than 2')
                # print('-----------')
                # print('median pro is {}'.format(self.median_pro))
                random_doc_id = random.randint(0, self.train_length)

                return random_doc_id, -1
            else:
                # print('-----------')
                # print('\033[1mCurr num docs labeled {}\033[0m'.format(self.num_docs_labeled))
                # print('-----------')
                # return 
                # return random.randint(0, len(self.median_pro)-1)
                if use_min:
                    chosen_idx = np.argmin(self.scores)
                else:
                    chosen_idx = np.argmax(self.scores)
                

                '''
                Don't show the users an already shown document
                '''
                while chosen_idx in self.recommended_doc_ids:
                    # self.scores = np.delete(self.scores, max_idx)
                    if use_min:
                        self.scores[chosen_idx] = float('inf')
                    else:
                        self.scores[chosen_idx] = -1
                    try:
                        if use_min:
                            chosen_idx = np.argmin(self.scores)
                        else:
                            chosen_idx = np.argmax(self.scores)
                    except:
                        print('current len of the score list is {}'.format(len(self.scores)))
                

                print('Classifier in progess...')
                print('\033[1mScore of the current document is {}\033[0m'.format(self.scores[chosen_idx]))
                self.recommended_doc_ids.add(chosen_idx)
                return chosen_idx, self.scores[chosen_idx]


    def recommend_document(self):
        document_id, score = self.preference()
        print(self.classes)
        return document_id, score


    def is_labeled(self, doc_id):
        return doc_id in self.user_labels

    def update_classifier(self):
        if self.mode == 1:
            # print('doc topic prob shape {}'.format(self.doc_topic_prob.shape))
            guess_label_probas = self.classifier.predict_proba(self.text_vectorizer[0:self.train_length])
            guess_label_logprobas = self.classifier.predict_log_proba(self.text_vectorizer[0:self.train_length])

            # Change this part
            scores = -np.sum(guess_label_probas*guess_label_logprobas*self.doc_topic_prob[:,:1], axis = 1)

            self.scores = scores
        else:
            guess_label_probas = self.classifier.predict_proba(self.text_vectorizer[0:self.train_length])
            guess_label_logprobas = self.classifier.predict_log_proba(self.text_vectorizer[0:self.train_length])
            scores = -np.sum(guess_label_probas*guess_label_logprobas, axis = 1)
            self.scores = scores

    def label(self, doc_id, user_label):
        # if self.mode == 1:
        if True:
            # print('START LABELLING')
            # print('\033[1mmode1\033[0m')
            # print(type(label_num))
            # label_num = int(label_num)
            if self.is_labeled(doc_id):
                # if user_label in self.user_label_number_map:
                if user_label in self.classes:
                    # label_num = self.user_label_number_map[user_label]
                    self.user_labels[doc_id] = user_label
                    self.labels_track[self.id_vectorizer_map[doc_id]] = user_label
                    if len(self.classes) >= 2:
                        self.classifier.partial_fit(self.documents_track, self.labels_track, self.classes)
                        self.update_classifier()
                        if global_classifier:
                            self.global_classifier.partial_fit(self.documents_track, self.labels_track, self.global_classes)
                else:
                    # label_num = len(self.classes)
                    # self.user_label_number_map[user_label] = label_num
                    # self.reverse_user_label_number_map[label_num] = user_label
                    self.user_labels[doc_id] = user_label
                    self.classes.append(user_label)
                    self.labels_track[self.id_vectorizer_map[doc_id]] = user_label
                    if len(self.classes) >= 2:
                        self.classifier = self.initialize_classifier('logreg')
                        self.classifier.partial_fit(self.documents_track, self.labels_track, self.classes)
                        self.update_classifier()  
                        if global_classifier:
                            self.global_classifier.partial_fit(self.documents_track, self.labels_track, self.global_classes)
            elif user_label in self.classes:  
                # print('all labels have, keep classes same but increase documents')
                # label_num = self.user_label_number_map[user_label]   
                self.user_labels[doc_id] = user_label
                self.id_vectorizer_map[doc_id] = self.num_docs_labeled
                # print(self.id_vectorizer_map)
                '''
                Adding documents and labels and track them
                '''
                self.labels_track.append(user_label)
                # self.id_vectorizer_map[doc_id] = len(self.labels_track-1)
                # self.documents_track.append(self.docs[doc_id])
                if self.text_vectorizer == None:
                    self.documents_track = self.text_vectorizer[doc_id]
                else:
                    self.documents_track = vstack((self.documents_track, self.text_vectorizer[doc_id]))
                
                if len(self.classes) < 2:
                    if self.mode == 1:
                        # self.update_median_prob(label_num)
                        self.update_median_prob(self.last_recommended_topic)
                else:
                    # print('-----------')
                    # print('start incremental learning')
                    # print('-----------')
                    self.classifier.partial_fit(self.documents_track, self.labels_track, self.classes)
                    # self.classifier.partial_fit(self.text_vectorizer[doc_id], [label_num], self.classes)

                    self.update_classifier()
                    if global_classifier:
                            self.global_classifier.partial_fit(self.documents_track, self.labels_track, self.global_classes)
                    

                self.num_docs_labeled += 1

                print('\033[1mnum docs labeled {}\033[0m'.format(self.num_docs_labeled))
            else:
                # print('\033[1mImplement this part: Creating a new label\033[0m')
                # label_num = len(self.classes)
                self.classes.append(user_label)
                self.id_vectorizer_map[doc_id] = self.num_docs_labeled
                # self.user_label_number_map[user_label] = user_label
                # self.reverse_user_label_number_map[label_num] = user_label
                # self.curr_label_num.append(label_num)
                self.user_labels[doc_id] = user_label

                self.labels_track.append(user_label)
                if self.text_vectorizer == None:
                    self.documents_track = self.text_vectorizer[doc_id]
                else:
                    self.documents_track = vstack((self.documents_track, self.text_vectorizer[doc_id]))

                if len(self.classes) < 2:
                    if self.mode == 1:
                        # self.update_median_prob(label_num)
                        self.update_median_prob(self.last_recommended_topic)
                else:
                    # print('-----------')
                    # print('start incremental learning')
                    # print('-----------')
                    self.classifier = self.initialize_classifier('logreg')
                    self.classifier.partial_fit(self.documents_track, self.labels_track, self.classes)
                    # self.classifier.partial_fit(self.text_vectorizer[doc_id], [label_num], self.classes)

                    self.update_classifier()
                    if global_classifier:
                            self.global_classifier.partial_fit(self.documents_track, self.labels_track, self.global_classes)
                    

                self.num_docs_labeled += 1
        
    
    def predict_label(self, doc_id):
        doc_id = int(doc_id)
        # print('user_label_number_map is {}'.format(self.user_label_number_map))
        if len(self.classes) >= 2:
            classes = self.classifier.classes_
            probabilities = self.classifier.predict_proba(self.text_vectorizer[doc_id])[0]
            sorted_indices = probabilities.argsort()[::-1]
            top_three_indices = sorted_indices[:3]
            

            # result = self.classifier.predict(self.text_vectorizer[doc_id])[0]
            result = ''
            for ele in top_three_indices:
                # result += classes[ele] + '    Confidence: ' + str(round(probabilities[ele], 2)) + '\n'
                result += classes[ele] + ','
            

            return result
        else:
            return "Model suggestion starts after two distinct labels are created two labels to start active learning"
        
    def eval_classifier(self):
        local_training_preds = self.classifier.predict(self.documents_track)
        local_training_acc = accuracy_score(self.labels_track, local_training_preds)
        local_testing_acc = -1
        if len(self.classes) >= 20 and global_classifier and global_testing:
            local_testing_preds = self.classifier.predict(self.test_texts)
            local_testing_acc = accuracy_score(self.test_labels, local_testing_preds)

            print('local testing accuracy score is {}'.format(local_testing_acc))
        else:
            local_testing_acc = -1

        if global_classifier:
            global_training_preds = self.global_classifier.predict(self.text_vectorizer[0:self.train_length])
            global_training_acc = accuracy_score(self.df.label.values.tolist()[0:self.train_length], global_training_preds)
            
            global_testing_acc = -1
            if global_testing:
                global_testing_preds = self.classifier.predict(self.test_texts)
                global_testing_acc = accuracy_score(self.test_labels, global_testing_preds)
                print('global testing accuracy score is {}'.format(global_testing_acc))

            print('global training accuracy score is {}'.format(global_training_acc))
            
        else:
            global_training_acc = -1
            global_testing_acc = -1

        # labels = self.df.label.values.tolist()
        # groud_truth = [self.user_label_number_map[ele] for ele in labels]
        # logreg_y_pred= self.classifier.predict(self.text_vectorizer[0:500])
        # accuracy = accuracy_score(groud_truth, logreg_y_pred)

        print('local training accuracy score is {}'.format(local_training_acc))
        return local_training_acc, local_testing_acc, global_training_acc, global_testing_acc
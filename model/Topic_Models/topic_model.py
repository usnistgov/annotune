import tomotopy as tp
from tomotopy.utils import Corpus
from gensim.utils import simple_preprocess
import pickle
from gensim.models import CoherenceModel
from gensim.corpora import Dictionary
from scipy.sparse import csr_matrix, hstack

import numpy as np
import pandas as pd
from pprint import pprint



class Topic_Model():
    '''
    If load model is false, then need to train the model
    If load moel is True, deirectly loads the model
    '''
    def __init__(self, num_topics, num_iters, model_type, load_data_path, train_len, user_labels, load_model, model_path):
        self.load_model = load_model
        if not load_model:
            self.num_topics = num_topics
            self.model_type = model_type
            self.load_data_path = load_data_path
            self.train_length = train_len
            self.num_iters = num_iters
            self.user_labels = user_labels
            self.doc_to_topics = None
            self.doc_topic_probas = None
            self.doc_topic_probas = None
            self.data_words_nonstop = None
        else:
            with open(model_path, 'rb') as inp:
                self.loaded_data = pickle.load(inp)

            # if model_type == 'LDA':
            #     self.model = tp.LDAModel.load(model_path.replace('pkl', 'bin'))
            # elif model_type =='SLDA':
            #     self.model = tp.SLDAModel.load(model_path.replace('pkl', 'bin'))
            self.document_probas = self.loaded_data['document_probas']
            self.doc_topic_probas = self.loaded_data['doc_topic_probas']
            self.topic_keywords = None
            self.model_type = model_type
            self.num_topics = num_topics

            self.data_words_nonstop = self.loaded_data['datawords_nonstop']
            self.word_spans = self.loaded_data['spans']
            # self.texts = self.loaded_data['texts']
            self.topics = self.loaded_data['topics']
            self.word_topic_distribution = self.loaded_data['word_topic_distribution']
            self.topic_reses = self.loaded_data['topic_reses']
            self.topic_res_nums = self.loaded_data['topic_res_nums']
            
    
    def convert_labels_to_numbers(self, label_list):
        label_mapping = {}
        next_label_number = 0
        numeric_labels = []

        for label in label_list:
            if label not in label_mapping:
                label_mapping[label] = next_label_number
                next_label_number += 1
            numeric_labels.append(label_mapping[label])

        return numeric_labels


    '''
    Train the topic model and save the data to save_data_path
    '''
    def train(self, save_data_path):

        # print('training...')
        print('num topics:', self.num_topics)
        with open(self.load_data_path, 'rb') as inp:
            saved_data = pickle.load(inp)

    
        datawords_nonstop = saved_data['datawords_nonstop']
        self.data_words_nonstop = datawords_nonstop
        spans = saved_data['spans']

        # corpus = Corpus()
        
        

        if self.model_type == 'LLDA':
            print('Created LLDA model')
            mdl = tp.LLDAModel(k=self.num_topics)

            print('Enumerating grams...')
            for i, ngrams in enumerate(datawords_nonstop):
                assert len(ngrams) != 0
                try:
                    mdl.add_doc(ngrams, [self.user_labels[i]] , ignore_empty_words=False)
                except Exception as e: 
                    print(e)
                    exit(0)

            
        elif self.model_type == 'SLDA':
            print('Created SLDA model')
            # Best hyperparameters: {'alpha': 0.43141738585649325, 'eta': 0.9614396430577419, 
            # 'min_cf': 2, 'min_df': 4, 'iterations': 145, 'var': 'l', 'glm_param': 5.252727047556928, 
            # 'nu_sq': 6.7920065058884145}

            # min_cf = 2; min_df = 4

            '''
            Map the user labels to numbers
            '''
           
            # nu_sq = [6.79]
            # glm_param = [5.25]
            # alpha = 0.43141738585649325; eta = 0.9614396430577419
            # nu_sq = [6.79 for i in range(len(user_label_set))]
            # glm_param = [5.252727047556928 for i in range(len(user_label_set))]
            # mdl = tp.SLDAModel(k=self.num_topics, vars=var_param, nu_sq=nu_sq,glm_param=glm_param)
            # mdl = tp.SLDAModel(k=self.num_topics, vars=var_param, min_cf= 2, min_df= 4, nu_sq=nu_sq,glm_param=glm_param)
            
            self.user_labels = dict(sorted(self.user_labels.items()))
            user_labels = list(self.user_labels.values())

            '''
            Need to convert the user labels from strings to integers as sLDA response vars
            '''
            user_label_map = self.convert_labels_to_numbers(user_labels)
            unique_user_values = np.unique(user_label_map)

            var_param = ['b' for i in range(len(unique_user_values))]
            indices = list(self.user_labels.keys())
            mdl = tp.SLDAModel(k=self.num_topics, vars=var_param, tw = tp.TermWeight.ONE, nu_sq= float('Inf'))
            # null_y = []

            '''
            user labels dictionary must have integer keys. The keys represent the document ID
            '''
            
            label_count = 0
            for i, ngrams in enumerate(datawords_nonstop):
                assert len(ngrams) != 0
                if i in indices:
                    # print('count', i)
                    y_user = [0 for _ in range(len(unique_user_values))]
                    y_user[user_label_map[label_count]] = 1
                    mdl.add_doc(ngrams,y=y_user)
                    label_count += 1
                else:
                    mdl.add_doc(ngrams, y=[0 for _ in range(len(unique_user_values))])   

            
            print('total user labels are', label_count)
                   
        elif self.model_type == 'LDA':
            print('Created LDA model')
            # Best hyperparameters: {'alpha': 0.1, 'eta': 1.0, 'min_cf': 4, 'min_df': 5, 'iterations': 173}
            # self.num_iters = 1730
            # mdl = tp.LDAModel(k=self.num_topics, alpha =0.05, eta=0.1, min_cf=4, min_df=5)
            # mdl = tp.LDAModel(k=self.num_topics, min_cf=4, min_df=5)
            mdl = tp.LDAModel(k=self.num_topics, tw = tp.TermWeight.ONE)
            
            for i, ngrams in enumerate(datawords_nonstop):
                # print(ngrams)
                assert len(ngrams) != 0
                mdl.add_doc(ngrams)
                
        elif self.model_type == "PLDA":
            mdl = tp.PLDAModel(latent_topics=self.num_topics, tw = tp.TermWeight.ONE)
            user_label_counter = 0
            for i, ngrams in enumerate(datawords_nonstop):
                assert len(ngrams) != 0
                if i in self.user_labels:
                    try:
                        mdl.add_doc(ngrams, [self.user_labels[i]] , ignore_empty_words=False)
                        user_label_counter += 1
                    except Exception as e: 
                        print(e)
                        exit(0)
                else:
                    try:
                        mdl.add_doc(ngrams, ignore_empty_words=False)
                    except Exception as e: 
                        print(e)
                        exit(0)
            
            print('total {} user labels for PLDA'.format(user_label_counter))
        else:
            raise Exception("unsupported model type!")
            
        
        

        print('starting training...')
        self.model = mdl
        # print('total # topics {}'.format(mdl.k))
        for i in range(0, self.num_iters, 10):
            # print('training iter {}'.format(i))
            mdl.train(10)

            if i % 300 == 0:
                print(f'Iteration: {i}, Log-likelihood: {mdl.ll_per_word}, Perplexity: {mdl.perplexity}, coherence: {self.get_coherence()}')
        
       
        
        # return
        # Instantiate a coherence model with the topic-word distribution, the corpus, and the dictionary
        coherence_score = self.get_coherence()

        print(coherence_score)
        '''
        Make documents for normal LDA
        '''
        self.maked_docs = []
        for doc in datawords_nonstop:
            curr_doc = mdl.make_doc(doc)
            self.maked_docs.append(curr_doc)


        # print(len(self.maked_docs))
        document_probas, doc_topic_probas = self.group_docs_to_topics()
        # print(document_probas)
        print(np.array(doc_topic_probas).shape)
        if not self.load_model:
            outs = self.print_topics()        
            topic_reses, topic_res_nums = [], []
            for index in range(len(self.maked_docs)):
                a, b = self.predict_doc_with_probs(index, outs)
                topic_reses.append(a)
                topic_res_nums.append(b)

            print('saving topic probabilities')
            result = {}
            # mdl.save(save_data_path.replace('pkl', 'bin'))
            result['document_probas'] = document_probas
            result['doc_topic_probas'] = doc_topic_probas
            result['spans'] = spans
            result['datawords_nonstop'] = saved_data['datawords_nonstop']
            # result['texts'] = len(saved_data['texts'])
            result['coherence'] = coherence_score
            result['topics'] = outs
            result['word_topic_distribution'] = self.get_word_topic_distribution()
            result['topic_reses'] = topic_reses
            result['topic_res_nums'] = topic_res_nums
            with open(save_data_path, 'wb+') as outp:
                pickle.dump(result, outp)
            
            self.load_model = True

    '''
    Returns
    doc_prob_topic: D X T matrix, where D is is the number of documents
    T is the number of topics from the topic model. For each document, it
    contains a list of topic probabilities.

    topics_probs: A dictionary, for each topic key, contains a list of tuples
    [(dic_id, probability)...]. Each tuple has a document id, representing 
    the row id of the document, and probability the document belong to this topic.
    For each topic, it only contains a list of documents that are the most likely 
    associated with that topic.
    ''' 
    def group_docs_to_topics(self):
        if not self.load_model:
            doc_prob_topic = []
            doc_to_topics, topics_probs = {}, {}
            for doc_id, doc in enumerate(self.maked_docs[0:self.train_length]):
                # if self.model_type == 'SLDA':
                #     inferred = self.model.estimate(doc)
                # else:
                if self.model_type == 'LLDA' and doc_id % 3000 == 0:
                    print('predicting probability on index ', doc_id)

                inferred, _ = self.model.infer(doc, iter=500)

                doc_topics = list(enumerate(inferred))
                doc_prob_topic.append(inferred)
                        

                # Infer the top three topics of the document
                doc_topics.sort(key = lambda a: a[1], reverse= True)
                        
                # print('doc topics {}'.format(doc_topics))
                doc_to_topics[doc_id] = doc_topics

                '''
                doc_topics[0][0] is the topic id. doc_topics[0][1] is doc id probability.
                '''
                if doc_topics[0][0] in topics_probs:
                    topics_probs[doc_topics[0][0]].append((doc_id, doc_topics[0][1]))
                else:
                    topics_probs[doc_topics[0][0]] = [(doc_id, doc_topics[0][1])]


            '''
            Sort the documents by topics based on their probability in descending order
            '''
            for k, v in topics_probs.items():
                topics_probs[k].sort(key = lambda a: a[1], reverse= True)

            self.doc_to_topics = doc_to_topics
            self.document_probas = topics_probs
            self.doc_topic_probas = doc_prob_topic
            return topics_probs, doc_prob_topic
        else:
            return self.document_probas, self.doc_topic_probas
    
    '''
    Print the list of topics for the topic model
    '''
    def print_topics(self, verbose=False):
        if not self.load_model:
            mdl = self.model
            out_topics = dict()
    
            # print(self.model_type == 'LDA')
            # print('label len is {}'.format(len(labels)))
            for k in range(mdl.k):
                topic_words = [tup[0] for tup in mdl.get_topic_words(k, top_n=30)]
                if verbose:
                    print(topic_words)

                out_topics[k] = topic_words
            
            return out_topics
        else:
            if verbose:
                for k, v in self.topics.items():
                    print('Topic ', k)
                    print(v)
            return self.topics
    

    def get_coherence(self):
        dictionary = Dictionary(self.data_words_nonstop)
        model_keywords = self.print_topics()

        keywords = []
        for k, v in model_keywords.items():
            keywords.append(v)

        coherence_model = CoherenceModel(
        topics=keywords,
        texts=self.data_words_nonstop,
        dictionary=dictionary,
        coherence='u_mass'
        )

        coherence_score = coherence_model.get_coherence()
        return coherence_score
    
    def get_word_topic_distribution(self):
        if not self.load_model:
            '''
            Data structure
            {
            [word1]: [topic1, topic2, topic3...]
            [word2]: [topic1, topic2, topic3...]
            [word3]: [topic1, topic2, topic3...]
            ...
            }
            '''

            # vocabs = self.model.vocabs
            vocabs = self.model.used_vocabs
            topic_dist = dict()

            for i in range(self.num_topics):
                topic_dist[i] = self.model.get_topic_word_dist(i)
            
            # print(vocabs[0])
            # print(vocabs[-1])
            print(len(topic_dist[0]))
            # print(len(vocabs))
            print(len(self.model.used_vocabs))
            word_topic_distribution = dict()
            for i, word in enumerate(vocabs):
                word_topic_distribution[word] = [v[i] for k, v in topic_dist.items()]

            self.word_topic_distribution = word_topic_distribution

            return word_topic_distribution
        else:
            return self.word_topic_distribution
    
    '''
    Given a document, returns a list of topics and probabilities
    associated with each topic. Also return a list of keywords associated
    with each topic
    '''
    def predict_doc_with_probs(self, doc_id, topics):
        if not self.load_model:
            # inferred, _= self.model.infer(self.maked_docs[doc_id], iter=500)
            # inferred = self.doc_topic_probas[doc_id]

                
            # result = list(enumerate(inferred))
            
            # result = sorted(result, key=lambda x: x[1], reverse=True)
            # print(result)

            '''
            Use the saved result to speed up process
            '''
            result = self.doc_to_topics[doc_id]

            
            topic_res = [[str(k), str(v)] for k, v in result]
            
            topic_res_num = [(num, topics[num]) for num, prob in result]

            # topic_res_num = []
            # for num, prob in result:
            #     keywords = topics[num]
            #     # topic_word_res[str(num)] = keywords
            #     topic_res_num.append((num, keywords))

            # print(topic_res_num)

            return topic_res, topic_res_num
        else:
            return self.topic_reses[doc_id], self.topic_res_nums[doc_id]
    

    '''
    Given a topic model, returns the list of topic keywords and spans of the 
    keywords for each topic
    '''
    def get_word_span_prob(self, doc_id, topic_res_num, threthold):
        if threthold <= 0:
            return dict()
        
        doc = self.data_words_nonstop[doc_id]
        doc_span = self.word_spans[doc_id]
        
        result = dict()
        
        for ele in topic_res_num:
            topic = ele[0]
            result[str(topic)] = {}
            result[str(topic)]['spans'] = []
            # result[str(topic)]['score'] = []

        for i, word in enumerate(doc):
            
            for ele in topic_res_num:
                topic = ele[0]
                keywords = ele[1]

                '''
                This part (word in self.word_topic_distribution) might filter out a lot of the vocabularies
                '''
                if word in self.word_topic_distribution and self.word_topic_distribution[word][topic] >= threthold:
                    if len(doc_span[i])>0 and doc_span[i][0] <= len(self.texts[doc_id]) and doc_span[i][1] <= len(self.texts[doc_id]):
                        result[str(topic)]['spans'].append([doc_span[i][0], doc_span[i][1]])
                    # result[str(topic)]['score'].append(str(self.word_topic_distribution[word][topic]))
                result[str(topic)]['keywords'] = keywords

        return result
    

    def concatenate_keywords(self, topic_keywords, datawords):
        result = []
        for i, doc in enumerate(datawords):
            if i < len(self.data_words_nonstop):
                topic_idx = np.argmax(self.doc_topic_probas[i])
                keywords = topic_keywords[topic_idx]
                curr_ele = doc + keywords
                res_ele = ' '.join(curr_ele)
                result.append(res_ele)
            else:
                res_ele = ' '.join(doc)
                result.append(res_ele)
                
        return result
    
    '''
    Concatenate each document with the top keywords from the prominent topic 
    '''
    def concatenate_keywords_raw(self, topic_keywords, raw_texts):
        result = []

        for i, doc in enumerate(raw_texts):
            topic_idx = np.argmax(self.doc_topic_probas[i])
            keywords = topic_keywords[topic_idx]
            keywords_str = ' '.join(keywords)
            res_ele = doc + ' ' + keywords_str
            result.append(res_ele)
        
        return result
    
    '''
    Concatenate the topic probability distribution features with the
    features from the classifier
    '''
    def concatenate_features(self, features):
        
        if self.model_type != 'SLDA':
            result = hstack([features, csr_matrix(self.doc_topic_probas).astype(np.float64)], format='csr')
        else:
            result = hstack([features, csr_matrix(self.doc_topic_probas).astype(np.float64)], format='csr')
        return result

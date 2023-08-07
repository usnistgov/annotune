import tomotopy as tp
from tomotopy.utils import Corpus
from gensim.utils import simple_preprocess
import pickle
import os
import re
import argparse


import numpy as np
import pandas as pd
from pprint import pprint



class Topic_Model():
    def __init__(self, num_topics, num_iters, model_type, load_data_path, train_len, user_labels, load_model, model_path):
        self.load_model = load_model
        if not load_model:
            self.num_topics = num_topics
            self.model_type = model_type
            self.load_data_path = load_data_path
            self.train_length = train_len
            self.num_iters = num_iters
            self.user_labels = user_labels
            self.doc_topic_probas = None
            self.doc_topic_probas = None
        else:
            with open(model_path, 'rb') as inp:
                self.loaded_data = pickle.load(inp)

            if model_type == 'LDA':
                self.model = tp.LDAModel.load(model_path.replace('pkl', 'bin'))
            elif model_type =='SLDA':
                self.model = tp.SLDAModel.load(model_path.replace('pkl', 'bin'))
            self.document_probas = self.loaded_data['document_probas']
            self.doc_topic_probas = self.loaded_data['doc_topic_probas']
            # self.get_document_topic_dist = self.loaded_data['get_document_topic_dist']
            self.topic_keywords = None
            self.topic_word_dist = None
            self.model_type = model_type
            self.num_topics = num_topics

            self.data_words_nonstop = self.loaded_data['datawords_nonstop']
            self.word_spans = self.loaded_data['spans']
            self.texts = self.loaded_data['texts']
            self.maked_docs = [self.model.make_doc(ele) for ele in self.data_words_nonstop]

    def train(self, save_data_path):

        # print('training...')
        print('num topics:', self.num_topics)
        with open(self.load_data_path, 'rb') as inp:
            saved_data = pickle.load(inp)

    
        datawords_nonstop = saved_data['datawords_nonstop']
        spans = saved_data['spans']

        corpus = Corpus()
        labels = saved_data['labels']
        label_set = list(set(labels))
        if np.nan in label_set:
            label_set.remove(np.nan)
        if None in label_set:
            label_set.remove(None)
        if 'None' in label_set:
            label_set.remove('None')

        label_dict = dict()
        for i,label in enumerate(label_set):
            label_dict[label] = i
        if self.model_type == 'LLDA':
            print('Enumerating grams...')
            for i, ngrams in enumerate(self.datawords_nonstop):
                if labels and not labels[i] == 'None':
                    label = labels[i]
                    corpus.add_doc(ngrams, labels=[label])
                else:
                    corpus.add_doc(ngrams)
        elif self.model_type == 'LDA':
            '''
            Change something here
            '''
            for i, ngrams in enumerate(datawords_nonstop):
                corpus.add_doc(ngrams)
        elif self.model_type == 'SLDA':
            user_label_set = np.unique(list(self.user_labels.values()))
            user_label_dict = {}
            for i,label in enumerate(user_label_set):
                user_label_dict[label] = i

            indices = np.unique(list(self.user_labels.keys()))
            null_y = [np.nan for _ in range(len(user_label_set))]

            # user labels dictionary must have integer keys
            for i, ngrams in enumerate(datawords_nonstop):
                if i in indices:
                    y_user = [0 for _ in range(len(user_label_set))]
                    y_user[user_label_dict[label]] = 1
                    corpus.add_doc(ngrams,y=y_user)
                else:
                    corpus.add_doc(ngrams, y=null_y)

                # if i >=100:
                #     corpus.add_doc(ngrams, y=[np.nan])
                # elif i >100 and i <= 300:
                #     corpus.add_doc(ngrams,y=[1])
                # else:
                #     corpus.add_doc(ngrams,y=[0])
                # y = [0 for _ in range(len(label_set))]
                
                # # y = [3 for i in range(20)]
                # if labels and not labels[i] == 'None':
                #     label = labels[i]
                #     y[label_dict[label]] = 1
                #     corpus.add_doc(ngrams, y=y)
                #     # print(y)
                # else:
                #     corpus.add_doc(ngrams, y=null_y)
                            
        else:
            raise Exception("unsupported model type!")

        if self.model_type == 'LLDA':
            print('Created LLDA model')
            mdl = tp.LLDAModel(k=self.num_topics)
        elif self.model_type == 'SLDA':
            print('Created SLDA model')
            # Best hyperparameters: {'alpha': 0.43141738585649325, 'eta': 0.9614396430577419, 
            # 'min_cf': 2, 'min_df': 4, 'iterations': 145, 'var': 'l', 'glm_param': 5.252727047556928, 
            # 'nu_sq': 6.7920065058884145}

            min_cf = 2; min_df = 4
            var_param = ['l' for i in range(len(user_label_set))]
            # nu_sq = [6.79]
            # glm_param = [5.25]
            alpha = 0.1; eta = 0.01
            nu_sq = [5 for i in range(len(user_label_set))]
            glm_param = [1.1 for i in range(len(user_label_set))]
            mdl = tp.SLDAModel(k=self.num_topics, vars=var_param, nu_sq=nu_sq,glm_param=glm_param)
                    
        elif self.model_type == 'LDA':
            print('Created LDA model')
            # Best hyperparameters: {'alpha': 0.1, 'eta': 1.0, 'min_cf': 4, 'min_df': 5, 'iterations': 173}
            self.num_iters = 1730
            # mdl = tp.LDAModel(k=self.num_topics, alpha =0.05, eta=0.1, min_cf=4, min_df=5)
            mdl = tp.LDAModel(k=self.num_topics, alpha =0.05, eta=0.1)

        mdl.add_corpus(corpus)

        print('starting training...')

        # print('total # topics {}'.format(mdl.k))
        for i in range(0, self.num_iters, 10):
            # print('training iter {}'.format(i))
            mdl.train(10)
            print(f'Iteration: {i}, Log-likelihood: {mdl.ll_per_word}, Perplexity: {mdl.perplexity}')
        # mdl.train(self.num_iters)
        self.lda_model = mdl
        # print('length of corups is {}'.format(len(corpus)))

        assert len(corpus) == len(saved_data['texts'])
       

        # Instantiate a coherence model with the topic-word distribution, the corpus, and the dictionary
        coherence_model = tp.coherence.Coherence(
            corpus=mdl, coherence="c_v", top_n=10
        )

        print(coherence_model.get_score())
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

        if not self.load_model:
            result = {}
            mdl.save(save_data_path.replace('pkl', 'bin'))
            result['document_probas'] = document_probas
            result['doc_topic_probas'] = doc_topic_probas
            result['spans'] = spans
            result['datawords_nonstop'] = saved_data['datawords_nonstop']
            result['texts'] = saved_data['texts']
            # result['maked_docs'] = self.maked_docs
            # result['get_document_topic_dist'] = doc_topic
            with open(save_data_path, 'wb+') as outp:
                pickle.dump(result, outp)
            
            self.load_model = True

    def group_docs_to_topics(self):
        if not self.load_model:
            doc_prob_topic = []
            doc_to_topics, topics_probs = {}, {}
            for doc_id, doc in enumerate(self.maked_docs[0:self.train_length]):
                # if self.model_type == 'SLDA':
                #     inferred = self.lda_model.estimate(doc)
                # else:
                inferred, _ = self.lda_model.infer(doc)

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

            self.document_probas = topics_probs
            self.doc_topic_probas = doc_prob_topic
            return topics_probs, doc_prob_topic
        else:
            return self.document_probas, self.doc_topic_probas
    
    def print_topics(self, verbose=False):
        mdl = self.model
        out_topics = dict()
   
        # print(self.model_type == 'LDA')
        # print('label len is {}'.format(len(labels)))
        for k in range(mdl.k):
            topic_words = [tup[0] for tup in mdl.get_topic_words(k, top_n=20)]
            if verbose:
                print(topic_words)

            out_topics[k] = topic_words
        
        return out_topics
    
    # def group_docs_to_topics(self):
    #     return self.document_probas, self.doc_topic_probas
    
    def get_word_topic_distribution(self):
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
        print(len(vocabs))
        print(len(self.model.used_vocabs))
        word_topic_distribution = dict()
        for i, word in enumerate(vocabs):
            word_topic_distribution[word] = [v[i] for k, v in topic_dist.items()]

        self.word_topic_distribution = word_topic_distribution

        return word_topic_distribution
    
    def predict_doc_with_probs(self, doc_id, topics):
        # print(topics)
        # if self.model_type != 'SLDA':
        #     inferred, _= self.model.infer(self.maked_docs[doc_id])
        # else:
        #     inferred = self.model.estimate(self.maked_docs[doc_id])
        inferred, _= self.model.infer(self.maked_docs[doc_id])

            
        result = list(enumerate(inferred))
        # print(result)
        # result.sort(key = lambda a: a, reverse= True)
        result = sorted(result, key=lambda x: x[1], reverse=True)
        # print(result)
        topic_res = [[str(k), str(v)] for k, v in result]
        topic_res_num = []

        # topic_word_res = {}
        # print(self.topics)
        for num, prob in result:
            keywords = topics[num]
            # topic_word_res[str(num)] = keywords
            topic_res_num.append((num, keywords))

        # print(topic_res_num)
        return topic_res, topic_res_num
    
    def get_word_span_prob(self, doc_id, topic_res_num, threthold):
        if threthold <= 0:
            return dict()
        
        doc = self.data_words_nonstop[doc_id]
        doc_span = self.word_spans[doc_id]
        # print(doc_span)
        # self.word_topic_distribution
        result = dict()
        # if self.model_type == 'LDA':
        # for j in range(self.num_topics):
        #     result[str(j)] = []
        # for topic, keywords in topic_res_num:
        for ele in topic_res_num:
            topic = ele[0]
            # keywords = ele[1]
            result[str(topic)] = {}
            result[str(topic)]['spans'] = []
            # result[str(topic)]['score'] = []

        for i, word in enumerate(doc):
            # for topic in range(self.num_topics):
            # for topic, keywords in topic_res_num:
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
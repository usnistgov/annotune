import random
import pickle
import numpy as np
from gensim.models import CoherenceModel
from gensim.corpora import Dictionary
from scipy.sparse import csr_matrix, hstack

class Neural_Model():
    def __init__(self, model_path, data_path, dataset_dir):
        with open(model_path, 'rb') as inp:
            self.loaded_data = pickle.load(inp)

        # self.model = self.loaded_data['model']
        self.document_probas = self.loaded_data['document_probas']
        self.doc_topic_probas = self.loaded_data['doc_topic_probas']
        self.get_document_topic_dist = self.loaded_data['get_document_topic_dist']
        self.topic_word_dist = self.loaded_data['topic_word_dist']
        self.vocabulary = self.loaded_data['vocabulary']
        self.topics = self.loaded_data['model_topics']
        self.topic_keywords = None

        
        self.data_words_nonstop = self.loaded_data['datawords_nonstop']
        self.word_spans = self.loaded_data['spans']
        # self.texts = self.loaded_data['texts']
        self.word_topic_distribution = self.get_word_topic_distribution()

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
        return self.document_probas, self.doc_topic_probas


    
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

        topic_word_dist = self.topic_word_dist.transpose()
        topic_word_probas = {}
        for i, ele in enumerate(topic_word_dist):
            topic_word_probas[self.vocabulary[i]] = ele

        self.word_topic_distribution = topic_word_probas

    '''
    Print the list of topics for the topic model
    '''
    def print_topics(self, verbose=False):
        output_topics = {}
        max_words = 20

        topics = self.topics
        for i, ele in enumerate(topics):
            output_topics[i] = ele[:max_words]
            if verbose:
                print(ele)

        self.topic_keywords = output_topics

        return output_topics

    '''
    Coherence metric
    ''' 
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

    '''
    Given a document, returns a list of topics and probabilities
    associated with each topic. Also return a list of keywords associated
    with each topic
    '''
    def predict_doc_with_probs(self, doc_id, topics): 
        inferred = self.get_document_topic_dist[int(doc_id)]
            
        result = list(enumerate(inferred))
        
        result = sorted(result, key=lambda x: x[1], reverse=True)
        
        topic_res = [[str(k), str(v)] for k, v in result]
        topic_res_num = []

        
        for num, prob in result:
            keywords = self.topic_keywords[num]
            topic_res_num.append((num, keywords))

        
        return topic_res, topic_res_num
    
    '''
    Given a topic model, returns the list of topic keywords and spans of the 
    keywords for each topic
    '''
    def get_word_span_prob(self, doc_id, topic_res_num, threthold):
        if threthold <= 0:
            return dict()
        
        doc_id = int(doc_id)
        
        doc = self.data_words_nonstop[doc_id]
        doc_span = self.word_spans[doc_id]
        
        result = dict()
        
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
                # if self.word_topic_distribution[word][topic] >= threthold:
                try:
                    if word in self.word_topic_distribution and self.word_topic_distribution[word][topic] >= threthold:
                        if len(doc_span[i])>0 and doc_span[i][0] <= len(self.texts[doc_id]) and doc_span[i][1] <= len(self.texts[doc_id]):
                            result[str(topic)]['spans'].append([doc_span[i][0], doc_span[i][1]])
                        # result[str(topic)]['score'].append(str(self.word_topic_distribution[word][topic]))
                except:
                    result[str(topic)]['spans'].append([])

                result[str(topic)]['keywords'] = keywords

        return result

    def concatenate_keywords(self, topic_keywords, datawords):
        result = []
        for i, doc in enumerate(self.data_words_nonstop):
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
    Concatenate the features of the topic modes with the classifier encodings
    '''
    def concatenate_features(self, features):
        result = hstack([features, csr_matrix(self.doc_topic_probas).astype(np.float64)], format='csr')
        return result
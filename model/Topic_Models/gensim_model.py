from gensim import corpora, models
from pprint import pprint
import pickle 
import numpy as np
from gensim.corpora import Dictionary
from gensim.models import CoherenceModel
from gensim.models.callbacks import PerplexityMetric
from scipy.sparse import csr_matrix, hstack

class Gensim_Model():
    '''
    If load model is false, then need to train the model
    If load moel is True, deirectly loads the model
    '''
    def __init__(self, num_topics, num_iters, passes, load_model, load_path, save_path):
        if not load_model:
            self.num_topics = num_topics
            self.num_iters = num_iters
            self.passes = passes
            self.data_words_nonstop = None
            self.bow_corpus = None
            self.document_probas = None
            self.doc_topic_probas = None
            self.save_path = save_path
        else:
            with open(load_path, 'rb') as inp:
                self.loaded_data = pickle.load(inp)
            
            self.load_model = load_model
            self.document_probas = self.loaded_data['document_probas']
            self.doc_topic_probas = self.loaded_data['doc_topic_probas']
            self.save_path = save_path
    '''
    Train the topic model and save the data to save_data_path
    '''
    def train(self, save_data_path):

        # print('training...')
        print('num topics:', self.num_topics)
        with open(save_data_path, 'rb') as inp:
            saved_data = pickle.load(inp)

    
        datawords_nonstop = saved_data['datawords_nonstop']
        self.data_words_nonstop = datawords_nonstop
        spans = saved_data['spans']

        

        dictionary = corpora.Dictionary(datawords_nonstop)
        bow_corpus = [dictionary.doc2bow(doc) for doc in datawords_nonstop]
        self.bow_corpus = bow_corpus


        perplexity_logger = PerplexityMetric(bow_corpus, logger='shell')
        print('starting training...')
        lda_model = models.LdaModel(bow_corpus, num_topics=self.num_topics, id2word=dictionary, passes=self.passes, iterations = self.num_iters, callbacks=[perplexity_logger])

        
        self.model = lda_model
        
        
        coherence_score = self.get_coherence()

        print('Coherence', coherence_score)
        

        # print(len(self.maked_docs))
        document_probas, doc_topic_probas = self.group_docs_to_topics()
        # print(document_probas)
        print(np.array(doc_topic_probas).shape)

        result = {}
        # mdl.save(save_data_path.replace('pkl', 'bin'))
        result['document_probas'] = document_probas
        result['doc_topic_probas'] = doc_topic_probas
        with open(self.save_path, 'wb+') as outp:
            pickle.dump(result, outp)
        

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
            doc_prob_topic = [[0.0] * self.num_topics for _ in range(len(self.bow_corpus))]
            for doc_id, topic_probs in enumerate(self.model.get_document_topics(self.bow_corpus)):
                for topic_id, prob in topic_probs:
                    doc_prob_topic[doc_id][topic_id] = prob

            # for ele in doc_prob_topic:
            #     if len(ele) != 19:
            #         print(len(ele))

            doc_to_topics, topics_probs = {}, {}
            for doc_id, doc in enumerate(doc_prob_topic):


                inferred = doc_prob_topic[doc_id]

                doc_topics = list(enumerate(inferred))
                        

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


    
    '''
    Print the list of topics for the topic model
    '''
    def print_topics(self, verbose=False):
        mdl = self.model
        out_topics = dict()
           
        for topic_id in range(self.num_topics):
            topic_keywords = [keyword for keyword, _ in mdl.show_topic(topic_id, topn=30)]
            if verbose:
                print(topic_keywords)

            out_topics[topic_id] = topic_keywords
            
        return out_topics
        
    
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
        return None
        

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
        result = hstack([features, csr_matrix(self.doc_topic_probas).astype(np.float64)], format='csr')
        return result

import random
import pickle
import numpy as np

class Neural_Model():
    def __init__(self, model_path, data_path, dataset_dir):
        with open(model_path, 'rb') as inp:
            self.loaded_data = pickle.load(inp)

        self.model = self.loaded_data['model']
        self.document_probas = self.loaded_data['document_probas']
        self.doc_topic_probas = self.loaded_data['doc_topic_probas']
        self.get_document_topic_dist = self.loaded_data['get_document_topic_dist']
        self.topic_keywords = None
        self.topic_word_dist = None

        
        self.data_words_nonstop = self.loaded_data['datawords_nonstop']
        self.word_spans = self.loaded_data['spans']
        self.texts = self.loaded_data['texts']

    def get_topic_word_dist(self):
        topic_word_dist = self.model.get_topic_word_dist().cpu().numpy()
        topic_word_probas = {}
        for i, ele in enumerate(topic_word_dist):
            topic_word_probas[i] = {}
            for word_idx, word_prob in enumerate(ele):
                topic_word_probas[i][self.model.vocabulary[word_idx]] = word_prob

        self.topic_word_dist = topic_word_probas

    def print_topics(self, verbose=False):
        output_topics = {}

        topics = self.model.get_topics(20)
        for i, ele in enumerate(topics):
            output_topics[i] = ele
            if verbose:
                print(ele)

        self.topic_keywords = output_topics
        return output_topics
    
    def predict_doc_with_probs(self, doc_id, topics):
        # print(topics)
        
        inferred = self.get_document_topic_dist[int(doc_id)]
            
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
            keywords = self.topic_keywords[num]
            # topic_word_res[str(num)] = keywords
            topic_res_num.append((num, keywords))

        # print(topic_res_num)
        return topic_res, topic_res_num
    
    def get_word_span_prob(self, doc_id, topic_res_num, threthold):
        if threthold <= 0:
            return dict()
        
        doc_id = int(doc_id)
        # print('doc id {}'.format(doc_id))
        # print('word span length {}'.format(len(self.word_spans)))
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
                # if self.word_topic_distribution[word][topic] >= threthold:
                try:
                    if self.topic_word_dist[topic][word] >= threthold:

                        '''
                        改这里
                        '''
                        if len(doc_span[i])>0 and doc_span[i][0] <= len(self.texts[doc_id]) and doc_span[i][1] <= len(self.texts[doc_id]):
                            # result[str(topic)].append((doc_span[i], self.word_topic_distribution[word][topic]))
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
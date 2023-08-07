'''
This file processes the data for models to do topic model or active learning
'''
import pandas as pd
import spacy
import re
from spacy.lang.en.stop_words import STOP_WORDS
import pickle
import argparse
from sklearn.feature_extraction.text import TfidfVectorizer

class Preprocessing():
    def __init__(self, data_path):
        print('Processing data...')
        df = pd.read_json(data_path)
        self.df = df
        
        data = df.text.values.tolist()
        self.texts = data
        # print('Finish lemmatization')

        nlp = spacy.load('en_core_web_sm')
        # nlp.add_pipe('sentencizer')
        nlp.add_pipe('sentencizer')
                                
        docs = [nlp(x) for x in data]

        stop_words = STOP_WORDS
        self.data_words_nonstop, self.word_spans = [], []

        with open("newsgroup_removewords.txt") as f:
                words_to_remove = f.readlines()

        words_to_remove = [x.strip() for x in words_to_remove]
        new_words_to_remove = [j.replace('\'', '') for i in words_to_remove for j in i.split(',')]
        new_words_to_remove = [j.replace(' ', '') for j in new_words_to_remove]
        # self.stop_words.extend(new_words_to_remove)
        for word in new_words_to_remove:
            stop_words.add(word)

        # Use TF-IDF to remove boring words
        tf_idf_words = self.get_filtered_words(data, 3)

        #Creating and updating our list of tokens using list comprehension 
        if 'newsgroup' in data_path:
            for doc in docs:
                temp_doc = []
                temp_span = []
                for token in doc:
                    if not len(str(token)) == 1 and (re.search('[a-z0-9]+',str(token))) \
                        and not token.pos_ == 'PROPN' and not token.is_digit and not token.is_space \
                                                    and str(token).lower() not in stop_words:
                            temp_doc.append(token.lemma_)
                            temp_span.append((token.idx, token.idx + len(token)))
                self.data_words_nonstop.append(temp_doc)
                self.word_spans.append(temp_span)
        else:
            for doc in docs:
                temp_doc = []
                temp_span = []
                for token in doc:
                    if (re.search('[a-z0-9]+',str(token))) \
                        and not len(str(token)) == 1 and not token.is_digit and not token.is_space \
                            and str(token).lower() not in stop_words:
                        temp_doc.append(token.lemma_)
                        temp_span.append((token.idx, token.idx + len(token)))
                self.data_words_nonstop.append(temp_doc)
                self.word_spans.append(temp_span)
        
        filtered_datawords_nonstop = [[''.join(char for char in tok if char.isalpha() or char.isspace()) for tok in doc] for doc in self.data_words_nonstop]
        self.data_words_nonstop = filtered_datawords_nonstop
        self.labels = df.label.values.tolist()
    
    def get_filtered_words(self, text, threthold):
        vectorizer = TfidfVectorizer()

        vectorizer.fit(text)
        # Get feature names and their idf values
        feature_names = vectorizer.get_feature_names_out()
        idf_values = vectorizer.idf_
        low_importance_words = [word for word, idf in zip(feature_names, idf_values) if idf <= threthold]
        return low_importance_words

    def save_data(self, save_path):
         print('saving data...')
         print(self.data_words_nonstop[0])
         result = {}
         result['datawords_nonstop'] = self.data_words_nonstop
         result['spans'] = self.word_spans
         result['texts'] = self.texts
         result['labels'] = self.labels
         with open('./Data/{}.pkl'.format(save_path), 'wb+') as outp:
                    pickle.dump(result, outp)

    def convert_clean_data_to_json(self, save_path):
        processed_test_data = [' '.join(doc) for doc in self.data_words_nonstop]
        result = []
        for i in range(len(processed_test_data)):
            curr = {'texts': processed_test_data[i], 'label': self.labels[i]}
            result.append(curr)

        df = pd.DataFrame(result)

        df.to_json(save_path, orient='records', lines=False)

def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--doc_dir", help="Where we read the source documents",
                       type=str, default="./Data/newsgroup_sub_500.json", required=False)
    argparser.add_argument("--save_path", help="Whether we save the data",
                       type=str, default='newsgroup_sub_500_processed', required=False)
    
    args = argparser.parse_args()
    process_obj = Preprocessing(args.doc_dir)
    # process_obj.convert_clean_data_to_json('./Data/processed_nist_all_labeled_1000.json')
    process_obj.save_data(args.save_path)

if __name__ == "__main__":
    main()
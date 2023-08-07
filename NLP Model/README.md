# NLP Topic Models

## Run Interface Locally With Default Congressional Bill Dataset and trained LDA model

```
flask run -p <your port number>
```

## Pipeline

1. Data Preprocessing (Tokenizing words, and save tokenized passages as a pickle file. A new copy of the json file with any passsages that have length 0 after tokenization will be removed and saved)

      To process a dataset, first please provide a dataset in json format that could be read by [pandas](https://pandas.pydata.org/docs/reference/api/pandas.read_json.html)

      The table must be contain the following columns

      | text | label |  sub_labels |
    | --------------- | --------------- | --------------- |
    | Text Passages    |  Major Topic | Minor Topic |
   
    
    To process the data, run the following. To process your own dataset, run `python data_process.py --help` to see the arguments
  ```
  cd Topic_Models
  python data_process.py 
  ```

2. Topic Model Training


   To train a topic model, run
```
cd Topic_Models

python train_save_topic_model.py --num_topics <number_of_topics> \ 
--num_iters <number_of_training_iterations> \
--model_type <LDA_or_SLDA_or_ETM> \
--load_data_path <Processed_pickle_data_path>
--num_topics <number_of_topics>
```

   The trained topic models will be saved to './Topic_Models/Model/' directory. 
   The saved models will be in a pickle format '{model_type}_{number of topics}.pkl'

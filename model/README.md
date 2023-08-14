# Document Annotation App

Welcome to the Document Annotation NLP Tool – an NLP topic modeling tool with active learning, designed to streamline document labeling.

## Getting Started

To run the app interface locally with the default Congressional Bill dataset, follow these steps:

1. Open your terminal.
2. Navigate to the `flask_app` directory using the `cd` command.
3. Run the following command, replacing `<your port number>` with your desired port number:

```
cd flask_app
flask run -p <your port number>
```

To process your own dataset, run the following command to see the available arguments and options:

```
python data_process.py --help
```

## Dataset Information

This app supports two datasets:

1. **20newsgroup**: A dataset of newsgroup documents.
2. **congressional_bill_project_dataset**: A dataset of Congressional Bill documents.

For the Congressional Bill dataset, the app uses data from the following sources:
- [Comparative Agendas Project](https://www.comparativeagendas.net/us)
- [Congressional Bills](http://www.congressionalbills.org)

To align topics with labels, refer to the [Codebook](https://comparativeagendas.s3.amazonaws.com/codebookfiles/Codebook_PAP_2019.pdf).

## Run in Colab

You can also access the app using Google Colab. Click the badge below to open the app notebook:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Pinafore/2023-document-annotation/blob/working-app/synthetic_experiment.ipynb)

## Pipeline

### Step 1: Data Preprocessing

To preprocess your dataset for analysis, follow these steps:

1. Ensure your dataset is in JSON format, readable by [pandas](https://pandas.pydata.org/docs/reference/api/pandas.read_json.html).
2. Your dataset table should have the columns: `text`, `label`, and `sub_labels`.
3. Run the preprocessing script:

  ```
  cd Topic_Models
  python data_process.py 
  ```

### Step 2: Topic Model Training

Choose from a range of topic models and train them using your preprocessed data:

- LDA (Latent Dirichlet Allocation)
- Supervised LDA
- Embedded Topic Model
- Contextualized Topic Model
- Bertopic
- Partially Labeled LDA
- Labeled LDA

Run the training script with appropriate arguments:

```
cd Topic_Models

python train_save_topic_model.py --num_topics <number_of_topics> \ 
--num_iters <number_of_training_iterations> \
--model_type <LDA_or_SLDA_or_ETM_or_CTM_or_Bertopic_or_PLDA_or_LLDA> \
--load_data_path <Processed_pickle_data_path>
--num_topics <number_of_topics>
--raw_text_path <json_file_path_filtered_by_data_process.py>
```

### Step 3: Synthetic Experiment

To reproduce the synthetic experiment, first train your model using Step 1 or Step 2. Then, open `synthetic_experiment.ipynb` to run the models.

### Step 4: Plotting Results

To visualize the synthetic experiment results, navigate to `new_model_plot.ipynb`. This notebook allows you to read and plot the saved results.

### Trained Topic Models

All trained topic models are saved in the `./Topic_Models/Model/` directory. Model files are stored in pickle format and follow the naming convention: `{model_type}_{number_of_topics}.pkl`. For instance, you might find files like `LDA_20.pkl`.

## Acknowledgements

This project was built upon the work of the following repositories:

- [Embedded Topic Model Repository](https://github.com/lffloyd/embedded-topic-model/tree/main)
- [Contextualized Topic Models Repository](https://github.com/MilaNLProc/contextualized-topic-models)
- [BERTopic Repository](https://github.com/MaartenGr/BERTopic/tree/master)
- [tomotopy Repository](https://github.com/bab2min/tomotopy)

We extend our gratitude to the authors of these original repositories for their valuable contributions and inspiration.




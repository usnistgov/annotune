import pandas as pd
from plotnine import ggplot, aes, geom_line, theme_minimal, ggtitle
import warnings
from plotnine.exceptions import PlotnineWarning
import sqlite3
import numpy as np


def plot(save_path, data_structure):
    # Example dataset
    key_list = list(data_structure.keys())
    x_axis = key_list[0]
    y_axis = key_list[1]
    color_group = key_list[2]

    df = pd.DataFrame(data_structure)

    # Create a line plot of training iterations vs. accuracy
    accuracy_plot = (
    ggplot(df, aes(x=x_axis, y=y_axis, color=color_group, group=color_group))
    + geom_line()
    + theme_minimal()
    + ggtitle('Numer of documents labeled vs. Training Accuracy for Multiple Models')
    )
    # Print the plot to the console
    print(accuracy_plot)

    # Save the plot to a file, suppressing the warnings
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', PlotnineWarning)
        accuracy_plot.save(save_path, dpi=300, width=6, height=4)


'''
Read all recommendations and print them on terminal
'''
def read_all_recommendations(db_name, topic_info):
    if topic_info:
        with sqlite3.connect(db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT user_id, topic_information FROM recommendations ')
            rows = cursor.fetchall()

            for row in rows:
                user_id = row[0]
                topic_information = row[1]

                print('user_id:', user_id)
                print('topic_information:', topic_information)
                print('---')
    else:
        with sqlite3.connect(db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT user_id, label, doc_id, response_time FROM recommendations')
            rows = cursor.fetchall()

            for row in rows:
                user_id = row[0]
                label = row[1]
                doc_id = row[2]
                response_time = row[3]

                print('user_id:', user_id)
                print('label:', label)
                print('doc_id:', doc_id)
                print('response_time:', response_time)
                print('---')


def read_all_users(db_name):
    with sqlite3.connect(db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT user_id, mode FROM users ')
            rows = cursor.fetchall()

            for row in rows:
                user_id = row[0]
                mode = row[1]

                print('user_id:', user_id)
                print('mode:', mode)
                print('---')

'''
print all the user ids and the mode used for the user
'''
def print_users_and_modes(db_name):
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, mode FROM users")
        rows = cursor.fetchall()

    print("User ID | Mode")
    print("--------+------")
    for row in rows:
        user_id, mode = row
        print(f"{user_id:7} | {mode}")


'''
Read the accuracy stores for a user
'''
def read_accuracy_db(user_id, database, accuracy_type):
    conn = sqlite3.connect(database)
    
    cursor = conn.execute('SELECT {} FROM recommendations WHERE user_id = ?'.format(accuracy_type), (user_id,))

    # Fetch all rows with user_id = 1
    rows = cursor.fetchall()

    conn.close()

    accuracies = []
    for i, row in enumerate(rows):
        # print(row[0])
        accuracies.append(row[0])
        print('num doc: {}, {}: {}'.format(i, accuracy_type, row[0]))
    
    print('-'* 10)


    return accuracies

def read_user_accuracy_np(data_path):
    array = np.load(data_path)
    return array


def plot_comparison(id1, id2, db_name, acc_type, id1_name, id2_name, save_path):
    session1_acc = read_accuracy_db(id1, db_name, acc_type)
    session2_acc = read_accuracy_db(id2, db_name, acc_type)
    print(session1_acc[0:20])
    print(session2_acc[0:20])
    start_index = 0

    if id1 % 4 == 0:
        session1_acc.pop()
    if id2 % 4 == 0:
        session2_acc.pop()

    for i in range(len(session1_acc)):
        if session1_acc[i] < 0 and i > start_index:
            start_index = i
    
    for j in range(len(session2_acc)):
        if session2_acc[j] < 0 and j > start_index:
            start_index = j 

    print(start_index)
    start_index += 1
    min_len = len(session1_acc) -start_index

    data_to_plot = {    
                'number documents labeled': [i+1+start_index for i in range(min_len)] * 2,
                'training acc': session1_acc[start_index:]+ session2_acc[start_index:],
                'model': [id1_name] * min_len + [id2_name] * min_len

                }

    plot(save_path, data_to_plot)

def plot_all_metric_comparison(id1, id2, id3, id4, db_name, acc_type, id1_name, id2_name, id3_name, id4_name,save_path):
    session1_acc = read_accuracy_db(id1, db_name, acc_type)
    session2_acc = read_accuracy_db(id2, db_name, acc_type)
    session3_acc = read_accuracy_db(id3, db_name, acc_type)
    session4_acc = read_accuracy_db(id4, db_name, acc_type)
    print('lengths')
    print(len(session1_acc))
    print(len(session2_acc))
    print(len(session3_acc))
    print(len(session4_acc))

    print(session1_acc[0:20])
    print(session2_acc[0:20])
    start_index = 0


    for i in range(len(session1_acc)):
        if session1_acc[i] < 0 and i > start_index:
            start_index = i
    
    for j in range(len(session2_acc)):
        if session2_acc[j] < 0 and j > start_index:
            start_index = j 

    for j in range(len(session3_acc)):
        if session3_acc[j] < 0 and j > start_index:
            start_index = j

    for j in range(len(session4_acc)):
        if session4_acc[j] < 0 and j > start_index:
            start_index = j        

    print(start_index)
    start_index += 1
    min_len = len(session1_acc) -start_index

    data_to_plot = {    
                'number documents labeled': [i+1+start_index for i in range(min_len)] * 4,
                'training acc': session1_acc[start_index:]+ session2_acc[start_index:]+session3_acc[start_index:]+ session4_acc[start_index:],
                'model': [id1_name] * min_len + [id2_name] * min_len + [id3_name] * min_len + [id4_name] * min_len

                }

    plot(save_path, data_to_plot)

def plot_all_metric_median_comparison(start, end, db_name, acc_type, id1_name, id2_name, id3_name, id4_name,save_path):
    mode0, mode1, mode2, mode3 = [], [], [], []
    for i in range(start, end):
        if i % 4 == 0:
            mode0.append(read_accuracy_db(i, db_name, acc_type))
        elif i % 4 == 1:
            mode1.append(read_accuracy_db(i, db_name, acc_type))
        elif i % 4 == 2:
            mode2.append(read_accuracy_db(i, db_name, acc_type))
        elif i % 4 == 3:
            mode3.append(read_accuracy_db(i, db_name, acc_type))

    mode0 = np.array(mode0)
    mode1 = np.array(mode1)
    mode2 = np.array(mode2)
    mode3 = np.array(mode3)
    # print('shapes')
    # print(mode0.shape)
    # print(mode1.shape)
    # print(mode2.shape)
    # print(mode3.shape)

    session1_acc = np.median(mode0, axis = 0)
    session2_acc = np.median(mode1, axis = 0)
    session3_acc = np.median(mode2, axis = 0)
    session4_acc = np.median(mode3, axis = 0)
    print('lengths')
    print(len(session1_acc))
    print(len(session2_acc))
    print(len(session3_acc))
    print(len(session4_acc))

    print(session1_acc[0:20])
    print(session2_acc[0:20])
    print(session3_acc[0:20])
    print(session4_acc[0:20])
    
    start_index = 0


    for i in range(len(session1_acc)):
        if session1_acc[i] < 0 and i > start_index:
            start_index = i
    
    for j in range(len(session2_acc)):
        if session2_acc[j] < 0 and j > start_index:
            start_index = j 

    for j in range(len(session3_acc)):
        if session3_acc[j] < 0 and j > start_index:
            start_index = j

    for j in range(len(session4_acc)):
        if session4_acc[j] < 0 and j > start_index:
            start_index = j        

    
    start_index += 1
    # print(start_index)
    min_len = len(session1_acc) -start_index

    # print('min len', min_len)
    # print(len([i+1+start_index for i in range(min_len)] * 4))
    # print(len(session1_acc[start_index:]+ session2_acc[start_index:]+session3_acc[start_index:]+ session4_acc[start_index:]))
    # print(len([id1_name] * min_len + [id2_name] * min_len + [id3_name] * min_len + [id4_name] * min_len))

    data_to_plot = {    
                'number documents labeled': [i+1+start_index for i in range(min_len)] * 4,
                 acc_type: list(session1_acc[start_index:])+ list(session2_acc[start_index:])+list(session3_acc[start_index:])+ list(session4_acc[start_index:]),
                'model': [id1_name] * min_len + [id2_name] * min_len + [id3_name] * min_len + [id4_name] * min_len

                }

    plot(save_path, data_to_plot)

def read_all_metrics(db_name,user_id):
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT local_training_acc, purity, RI, NMI FROM recommendations WHERE user_id = ?', (user_id,))
        rows = cursor.fetchall()

    print("User ID | train acc | purity | RI | NMI")
    print("--------+------+------+------+------")
    for row in rows:
        train_acc, purity, RI, NMI = row
        train_acc = round(train_acc, 3)
        purity = round(purity, 3)
        RI = round(RI, 3)
        NMI = round(NMI, 3)

        print(f"{user_id} | {train_acc}| {purity}| {RI}| {NMI}")


db_name = './07_06_2023_test.db'
with sqlite3.connect(db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT user_id, time, user_labels FROM user_label_track ')
            rows = cursor.fetchall()

            for row in rows:
                user_id = row[0]
                time= row[1]
                labels = row[2]

                print('user_id:', user_id)
                print('time_information:', time)
                print('labels', labels)
                print('---')


exit(0)
# database_name = '06_28_2023_100newsgroup_test.db'
# database_name = './06_29_2023_100newsgroup_test_concate_19_topics.db'
database_name = './06_29_2023_100newsgroup_test_concate_19_topics_added_user_metrics.db'
acc_type = 'local_training_acc'

# read_all_metrics(database_name, 4)
# print_users_and_modes(database_name)
# read_all_recommendations(database_name, False)
read_all_users(database_name)
# read_accuracy_db(5, database_name, acc_type)
# read_accuracy_db(4, database_name, 'purity')
exit(0)
# plot_comparison(3, 4, database_name, 'local_training_acc', 'ETM','LA', './plot_results/06_28_2023/100newsgroup/ETM_vs_LA_accuracy_noconcate.png')
# plot_all_metric_comparison(1, 2, 3, 4, database_name, 'RI', 'LDA', 'SLDA', 'ETM', 'LA', './plot_results/06_29_2023/100newsgroup/RI_concate.png')
plot_all_metric_median_comparison(1, 21, database_name, 'local_training_acc', 'LDA', 'SLDA', 'ETM', 'LA', './plot_results/06_29_2023/19_topics/100newsgroup/acc_concate_median5.png')

# 06-27    20 topics
'''
1: LDA concatenate features
2: SLDA concatenate features 
3: ETM concatenate features
4: Active Learning
5: LDA concatenate features
6: SLDA concatenate features fine tuining
7: ETM no concatenate features
8: Active Learning
9: LDA no concatenate features
10: SLDA no concatenate features
'''
# 06-28   06_28_2023_100newsgroup_test.db    13 topics
'''
1: LDA
2: SLDA
3: ETM
4: LA
5: LDA
6: SLDA
7: ETM concate
8: LA
9: LDA concate
10: SLDA concate
'''

# 06-28   06_28_2023_100newsgroup_test_no_concate.db    13 topics
'''
1. LDA no concate
2. SLDA no concate
3. ETM no concate
4. LA no concate
'''


# database_name = './06_28_2023_100newsgroup_test_concate_13_topics.db'
'''
13 topics, with classifier purity. Each group is over 15 runs. Total 60 users
'''





'''
Original      Concat          min_cf       hand_pick_hyperparam        opt+min_cf
1: LA         31: LA         
2: LDA        32: LDA        
3: SLDA       33: SLDA       62: SLDA      55: SLDA                     72: SLDA
4: ETM        34: ETM        
'''

# # exit(0)
# LA_session_acc = read_accuracy_db(31, database_name, acc_type)
# LDA_session_acc = read_accuracy_db(32, database_name, acc_type)
# SLDA_session_acc = read_accuracy_db(33, database_name, acc_type)

# ETM_session_acc = read_accuracy_db(4, database_name, acc_type)
# concate_ETM_session_acc = read_accuracy_db(34, database_name, acc_type)
# logistic_acc = read_user_accuracy_np('./np_files/classifier_results.npy')


# # min_len = min(len(logistic_acc[0]), len(logistic_acc[1]), len(logistic_acc[2]), len(logistic_acc[3]), len(LA_session_acc), len(LDA_session_acc))
# # LDA_session_acc[2] = 0.05
# # LDA_session_acc[3] = 0.05
# print(ETM_session_acc[20:30])
# print(LA_session_acc[20:30])
# # data_to_plot = {
# #                 'number documents labeled': [i+1 for i in range(min_len)] * 5,

# #                 'training acc': LA_session_acc[2:] + logistic_acc[2].tolist() + LDA_session_acc[2:] + SLDA_session_acc[2:] + ETM_session_acc[2:],
# #                 'model': ['LA session'] * min_len + ['ordered acc'] * min_len + ['LDA session'] * min_len + ['SLDA session'] * min_len + ['ETM session'] * min_len
# #                 }

# min_len = min(len(LA_session_acc[2:]), len(ETM_session_acc))
# data_to_plot = {    
#                 'number documents labeled': [i+3 for i in range(min_len)] * 2,
#                 'training acc': concate_ETM_session_acc[2:]+ ETM_session_acc[2:],
#                 'model': ['concat ETM'] * min_len + ['ETM fitting'] * min_len

#                 }

# save_path = './plot_results/EMT0_vs_ETM_optimize.png'
# plot(save_path, data_to_plot)
# print(logistic_acc[2])

'''
previous database names
database_name = 'local_users.db'
database_name = 'server_users.db'
database_name = './database/06_26_2023_newsgroup_test.db'
database_name = './database/06_27_2023_newsgroup_test.db'
'''
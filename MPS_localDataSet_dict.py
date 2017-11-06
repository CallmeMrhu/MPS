# major change: reject user_id or song_id to number with dict
# in the method of createCountArray(objPath_clean, threshold)


import numpy as np
import pandas as pd
import time


def extractSubDataSet_US(length, path, objPath_extract):
    # get subDataSet contains user_id column and song_id column
    # length : length of sub-dataset for every user
    # length==0 : all the dataset
    # path : path of DataSet
    # objPath_extract : path of extracting subDataSet of user-song
    reviews = pd.read_csv(path, sep='\t', header=None, error_bad_lines=False)
    for i in range(1, 1001):
        user_id = 'user_00' + str(i).zfill(4)
        reviews_id = reviews[0] == user_id
        filter_reviews = reviews[reviews_id]
        if length == 0:
            result = filter_reviews.iloc[:, :3]
        # sub-dataset
        else:
            result = filter_reviews.iloc[:length, :3]
        result.to_csv(objPath_extract, sep=',', header=False, index=False, mode='a')


def cleanDataSet(objPath_extract, objPath_clean):
    extractDataSet = pd.read_csv(objPath_extract, sep=',', header=None)
    extractDataSet_noDuplts = extractDataSet.drop_duplicates()
    cleanDataSet = extractDataSet_noDuplts.dropna()
    cleanDataSet.to_csv(objPath_clean, header=None, index=False)

    # print(df_noDup_noNull.shape)
    # show the count of different row
    # print(df_noDup)
    # calculate the count of null
    # print(df_noDuplts[0].isnull().value_counts())
    # print(df_noDuplts.shape)
    # print(df.shape)
    # print(df)
    # -------------------------
    # return cleanDataSet


# get user_dict(songs_dict)
def getEffectiveUserAndSongs(objPath_clean, threshold):
    df = pd.read_csv(objPath_clean, sep=',', header=None)
    # get the list of users and songs
    users_list = list(df[0].drop_duplicates())
    # songs_list = list(df[2].drop_duplicates())
    users_songs_df = df[[0, 2]].drop_duplicates()
    # print('len(users_songs_df)', len(users_songs_df))
    # create the dict of users and songs
    users_dict = {}
    songs_dict = {}
    # print(len(songs))
    # exclude user listened to less than threshold
    # exclude the songs which have been played by less than 'threshold' users
    value = 0
    for user in users_list:
        if len(df[df[0] == user]) >= threshold:
            users_dict[user] = value
            value += 1
    print('len(users_dict):',len(users_dict))
    # print(users_dict)

    value = 0
    songs_list = list(users_songs_df[2].drop_duplicates())
    # print('len(songs_list)', len(songs_list))
    for song in songs_list:
        if len(users_songs_df[users_songs_df[2] == song]) >= threshold:
            songs_dict[song] = value
            value += 1
    print('len(songs_dict)', len(songs_dict))
    return users_dict, songs_dict


def createCountArray(users_dict,songs_dict,objPath_clean):
    # exclude the users only listened to less than 10 songs
    # exclude the songs which have been played by less than 10 users
    df = pd.read_csv(objPath_clean, sep=',', header=None)
    users = list(df[0].drop_duplicates())
    # songs_over_threshold = list(df[2].drop_duplicates())
    # users_songs_list = []
    row = len(users_dict)
    column = len(songs_dict)
    R = np.zeros((row,column))

    for user in users[:20]:
        if user in users_dict.keys():
            users_dict_value = users_dict[user]
        else:
            continue
        user_songs_list = list(df[(df[0] == user)][2])
        for song in user_songs_list:
            if song in songs_dict.keys():
                songs_dict_value = songs_dict[song]
            else:
                continue
            R[users_dict_value][songs_dict_value]+=1

    np.savetxt('Result/resultMatrix_dict.csv', R, delimiter=',', fmt='%d')

    return R


def createSequence(objPath_clean, threshold):
    # using cleaning-data
    # building songs sequence
    # according to user_id timestamp songs_id
    # without more than 800s interruption
    # every sequnce contains more than 10 songs;threshold means 10 there
    cleanDataSet = pd.read_csv(objPath_clean, sep=',', header=None)
    file_result = open('Result/listenSession.txt', 'a')

    listen_session = []
    for j in range(1, 1001):
        user_id = 'user_00' + str(j).zfill(4)
        cleanDataSet_id = cleanDataSet[0] == user_id
        filter_cleanDataSet = cleanDataSet[cleanDataSet_id]
        filter_cleanDataSet_timastampList = filter_cleanDataSet[1].tolist()
        filter_cleanDataSet_songsList = filter_cleanDataSet[2].tolist()
        timestamplist_length = len(filter_cleanDataSet_songsList)
        # print(timestamplist_length)

        if timestamplist_length < threshold:
            continue
        current_sequence = []
        time_current = filter_cleanDataSet_timastampList[0]
        # print(time_current)
        for i in range(timestamplist_length - 1):
            # print(i)
            # print(current_sequence)
            current_sequence.append(filter_cleanDataSet_songsList[i])
            print('success')
            time_behind = filter_cleanDataSet_timastampList[i + 1]
            time_current_timestamp = timeTotimestamp(time_current)
            time_behind_timestamp = timeTotimestamp(time_behind)
            time_distance = abs(time_current_timestamp - time_behind_timestamp)
            # time_distance = 0
            print('the users:%d,time_distance:%d' % (j, time_distance))

            if i == (timestamplist_length - 2):
                if time_distance > 800:
                    if len(current_sequence) >= threshold:
                        file_result.write(str(current_sequence))
                        # listen_session.append(current_sequence)
                else:
                    current_sequence.append(filter_cleanDataSet_songsList[i + 1])
                    if len(current_sequence) >= threshold:
                        file_result.write(str(current_sequence))
                        # listen_session.append(current_sequence)
                break
            else:
                if time_distance > 800:
                    if len(current_sequence) >= threshold:
                        file_result.write(str(current_sequence))
                        # listen_session.append(current_sequence)
                    current_sequence = []
                    # current_sequence.append(filter_cleanDataSet_songsList[i + 1])
                # if <=800 continue
                time_current = time_behind

    file_result.close()
    # return listen_session


def getPathAndThreshold(length, threshold):
    length = length
    path = 'lastfm-dataset-1K/userid-timestamp-artid-artname-traid-traname.tsv'
    objPath_extract = 'Result/userid-timestamp-artid-' + str(length) + '-extract.csv'
    objPath_clean = 'Result/userid-timestamp-artid-' + str(length) + '-clean.csv'
    threshold = threshold
    return path, objPath_extract, objPath_clean, threshold, length


def timeTotimestamp(datatime):
    timeArray = time.strptime(datatime, '%Y-%m-%dT%H:%M:%SZ')
    timestamp = time.mktime(timeArray)
    return timestamp


if __name__ == '__main__':
    # length for sub-DataSet,every user listens to 'length' songs
    # length = 20
    # threshold = 0

    length = 0
    threshold = 10


    path, objPath_extract, objPath_clean, threshold, length = getPathAndThreshold(length, threshold)

    # path = 'lastfm-dataset-1K/userid-timestamp-artid-artname-traid-traname.tsv'
    # objPath_extract = 'lastfm-dataset-1K/userid-timestamp-artid-' + str(length) + '-extract.csv'
    # objPath_clean = 'lastfm-dataset-1K/userid-timestamp-artid-' + str(length) + '-clean.csv'



    # extractSubDataSet_US(length, path, objPath_extract)
    # cleanDataSet = cleanDataSet(objPath_extract, objPath_clean)

    users_dict, songs_dict = getEffectiveUserAndSongs(objPath_clean, threshold)

    createCountArray(users_dict,songs_dict,objPath_clean)
    # createSequence(objPath_clean, threshold)
    # getEffectiveUserAndSongs(objPath_clean)

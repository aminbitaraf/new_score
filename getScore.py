import requests
import hashlib
import pandas as pd
import os
import time

URL = "http://puya.kashmar.ac.ir/gateway/UserInterim.php"
EXAM_SCORE_URL = 'http://puya.kashmar.ac.ir/educ/educfac/stuShowEducationalLogFromGradeList.php'
TIMES_TO_CHECK_PER_MIN = 0.2

username = input('Enter your username: \n')
password = input('Enter your password: \n')
hashPass = hashlib.md5(password.encode()).hexdigest()

postParam = {
    'UserPassword' : hashPass,
    'UserID' : username,
}

def get_score(PHPSESSID):
    response = requests.post(EXAM_SCORE_URL,cookies={'PHPSESSID':PHPSESSID})
    
    if len(response.text) == 251:
        PHPSESSID = get_PHPSESSID()
        response = requests.post(EXAM_SCORE_URL,cookies={'PHPSESSID':PHPSESSID})

    tableBody = pd.read_html(response.text)
    return tableBody[0][['نام درس','نمره']].dropna()


def get_PHPSESSID():
    with requests.Session() as s:
        s.post(URL, data=postParam)
        if not s.cookies:
            raise print('your password or username is wrong')

        PHPSESSID = s.cookies.get_dict()['PHPSESSID']
        f = open('PHPSESSID.txt','w')
        f.write(PHPSESSID)
        f.close()
        return PHPSESSID

get_PHPSESSID()

while True:
    readPHPSESSID = open('PHPSESSID.txt','r')
    PHPSESSID = readPHPSESSID.readline()
    readPHPSESSID.close()

    if not PHPSESSID:
        get_PHPSESSID()

    if not os.path.exists('./Score.csv'):
        get_score(PHPSESSID).to_csv('Score.csv',index=False)
    
    oldScore = pd.read_csv('./Score.csv')
    newScore = get_score(PHPSESSID).reset_index().drop(columns=['index'])
    if not oldScore.equals(newScore):
        print('************YOU HAVE NEW SCORE!************')
        newScore.to_csv('Score.csv',index=False)
        break
    else:
        print('WE WORKING HARD')

    time.sleep(TIMES_TO_CHECK_PER_MIN * 60)

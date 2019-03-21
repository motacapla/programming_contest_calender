import re
import urllib.request
from bs4 import BeautifulSoup
import time
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


# DELETE
def delete_collection(coll_ref, batch_size):
    docs = coll_ref.limit(10).get()
    deleted = 0
    for doc in docs:
        print(u'Deleting doc {} => {}'.format(doc.id, doc.to_dict()))
        doc.reference.delete()
        deleted = deleted + 1
    if deleted >= batch_size:
        return delete_collection(coll_ref, batch_size)

# READ
def read_collection(ref):
    cnt = 0
    docs = ref.get()
    for doc in docs:
        print(u'{} => {}'.format(doc.id, doc.to_dict()))    
        cnt+=1
    return cnt

# AtCoderから「予定されたコンテスト」をスクレイピング
def get_atcoder_contests():
    url = "https://atcoder.jp/?lang=ja"
    html = urllib.request.urlopen(url)
    soup = BeautifulSoup(html, "html.parser")
    soup = soup.select_one("#collapse-contest")
    results = soup.find_all(["small","h4"])
    memo = False
    p1 = r"予定された"
    p2 = r"終了後"
    rep1 = re.compile(p1)
    rep2 = re.compile(p2)
    contests = []
    for res in results:
        text = res.string
        if(rep1.match(text)):
            memo = True    
        if(rep2.match(text)):
            memo = False
        if(memo):
            contests.append(res)
    p1 = r"\d{4}-\d{1,2}-\d{1,2}"
    rep1 = re.compile(p1)
    memo = False
    name = []
    date = []
    url = []
    for c in contests:
        text = c.string    
        matchOB = rep1.match(text)
        if(memo):
            memo = False
            url.append('https://atcoder.jp'+c.find("a").get("href"))
            name.append(text)
        if(matchOB):
            memo = True
            date.append(text.split('+')[0])

    return name, date, url

if __name__ == "__main__":
    name, date, url = get_atcoder_contests()
        
    # Using Cloud firestore
    # Use the application default credentials
    cred = credentials.Certificate('./ProconCalander-17f5e6fbc158.json')
    firebase_admin.initialize_app(cred)
    db = firestore.client()

    ref = db.collection(u'contests')
    cnt = read_collection(ref)

    # DELETE EVERHTHING if there is data!!
    if(cnt > 0):
        delete_collection(ref, 1)
    
    # CREATE
    for i in range(len(name)):
        ID = 'id'+ str(time.mktime(datetime.strptime(date[i], "%Y-%m-%d %H:%M:%S").timetuple()))
        doc_ref = db.collection(u'contests').document(ID)
        doc_ref.set({
            u'contest_name': 'AtCoder',            
            u'name': name[i],
            u'date': date[i],
            u'url':  url[i],
        })



    

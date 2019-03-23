import re
import urllib.request
from bs4 import BeautifulSoup
import time
#from datetime import datetime
import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import calendar

months = {}
debug = False

def init_convert_eng_month():
    for i, name in enumerate(calendar.month_abbr):
        if(i < 10):
            months[name] = '0'+str(i)
        else:
            months[name] = str(i)
        
def convert_eng_month(s):        
    tmp = s.split("/")[0]
    s = s.replace(tmp, months[tmp])
    return s


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
def get_yukicoder_contests():
    url = "https://yukicoder.me/contests"
    html = urllib.request.urlopen(url)
    soup = BeautifulSoup(html, "html.parser")
    soup = soup.select_one("#content")
    ress = soup.find_all(["tbody"],limit=2)[1]
    #print(ress)
    name = []
    date = []
    url = []    
    p1 = r"順位表へ"
    rep1 = re.compile(p1)
    for res in ress.find_all(["a"]):
        if(rep1.match(res.string)):
            continue
        name.append(res.string)
        url.append("https://yukicoder.me"+res.get("href"))

    tmp = []
    for i,res in enumerate(ress.find_all(["td"])):
        if(i % 2 == 1):
            tmp.append(str(res).replace(" ",""))   
    for i,res in enumerate(tmp):
        if(i % 2 == 0):
            res = res.split("〜")[0]
            res = res[5:]
            date.append('{0}{1}{2}'.format(res[:10], " ", res[10:]))

    return name, date, url

if __name__ == "__main__":
    name, date, url = get_yukicoder_contests()
    
    # Using Cloud firestore
    # Use the application default credentials
    cred = credentials.Certificate('./ProconCalander-17f5e6fbc158.json')
    firebase_admin.initialize_app(cred)
    db = firestore.client()

    ref = db.collection(u'contests')
    cnt = read_collection(ref)
    
    # CREATE
    for i in range(len(name)):
        ID = 'id'+ str(time.mktime(datetime.datetime.strptime(date[i], "%Y-%m-%d %H:%M:%S").timetuple()))
        doc_ref = db.collection(u'contests').document(ID)
        doc_ref.set({
            u'contest_name': 'yukicoder',
            u'title': name[i],
            u'date': date[i],
            u'url':  url[i],
        })

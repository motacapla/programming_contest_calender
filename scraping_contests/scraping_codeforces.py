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
def get_codeforces_contests():
    url = "https://codeforces.com/contests"
    html = urllib.request.urlopen(url)
    soup = BeautifulSoup(html, "html.parser")
    soup = soup.select_one("#pageContent > div > div.datatable > div:nth-of-type(6) > table")
    ress = soup.find_all(["td", "a"])

    name = []
    date = []
    url = []
    li = []
    p1 = r"Register*\w"
    p2 = r"[a-zA-Z]"
    rep1 = re.compile(p1)    
    rep2 = re.compile(p2)    
    for res in ress:
        text = res.string
        #print(text)
        #print(type(text))
        if(text == None):
            continue
        if(rep1.match(text)):
            li.append("https://codeforces.com/contests"+res.get("href"))
        else:
            li.append(text)

    p1 = r"http*\w"
    p2 = r"[a-zA-Z/]"    
    rep1 = re.compile(p1)        
    for l in li:
        l = l.replace("\r", "")
        l = l.replace("\n", "")
        l = l.replace(" ", "")
        if(debug):
            print(l)
        if(rep1.match(l)):
            url.append(l)
        elif(rep2.match(l)):
            name.append(l)
        else:
            continue
        
    for res in soup.find_all(["span"]):
        if(debug):
            print(res.string)
        if(rep2.match(res.string)):
            date.append(res.string)
        
    return name, date, url

def time_transfer(date, diff):  
    dt = datetime.datetime.strptime(date, '%m/%d/%Y %H:%M')
    dt = dt + datetime.timedelta(hours=diff)
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def cvrt(date, diff):
    res = []
    init_convert_eng_month()                
    for d in date:
        d = convert_eng_month(d)
        d = time_transfer(d, diff)
        res.append(d)
    return res

if __name__ == "__main__":
    name, date, url = get_codeforces_contests()

    date = cvrt(date, 6)

    if(debug):
        print(name,date,url)

    while(len(url) < len(name)):
        url.append("https://codeforces.com/contests")


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
            u'contest_name': 'Codeforces',
            u'name': name[i],
            u'date': date[i],
            u'url':  url[i],
        })

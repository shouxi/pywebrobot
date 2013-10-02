#-*- coding:utf-8 -*-

import urllib2
import time
import os
if 'SERVER_SOFTWARE' in os.environ:
    from bae.api import logging
else:
    import logging
    
from BeautifulSoup import BeautifulSoup
from xml.dom import minidom

from flask import Flask
app = Flask(__name__)

scie_rss = "Hello"

@app.route('/')
def root():
    return "Welcome!!\n"

@app.route('/<path>')
def other(path):
    return "can not find: " + path

@app.route('/get-scie-news.rss')
def rss_scienews():
    global scie_rss
    return scie_rss

@app.route('/update-scie-news.cmd')
def update_scie_news(watch_days = 7*24*60*60, newslist = {}):
    url = 'http://www.scie.uestc.edu.cn/'
    url_header = url + 'main.php?action=list&catId='
    catIds = ['14', '34', '73', '23']
    now = time.time()
    mktime = lambda x:time.mktime(time.strptime(x, "%Y-%m-%d %H:%M"))    
    
    for k in newslist:
        if newslist[k][1] + watch_days < now:
            del newslist[k]

    for catId in catIds:
        html = urllib2.urlopen(url_header+catId).read()
        soup = BeautifulSoup(html)
        lilist = soup.find('ul', {'class':"newslist"}).findAll('li')
        for li in lilist:
            href = url + li.a['href']
            #utf-8
            the_time = mktime(li.span.text)
            if the_time + watch_days > now:
                newslist[href] = (li.a.text, the_time)
    
    doc = minidom.Document()
    rss = doc.createElement('rss')
    rss.setAttribute('version', '2.0')
    doc.appendChild(rss)
    
    channel_info = {'title':u'电子科大通信学院通知公告订阅频道',
                    'link': u'http://www.scie.uestc.edu.cn/',
                    'description': u'订阅通知公告,重要信息不错过！目前只转发"学院公告", "学生科", "研管科", "科研科" 4个栏目内容',
                    'language': 'zh-cn',
                    'generator': 'rss-spider by rossini',
                    'docs': 'http://blogs.law.harvard.edu/tech/rss',
                    }
    channel = genRSSItem(doc, channel_info, tag='channel')
    rss.appendChild(channel)

    mkpubDate = lambda t: time.strftime("%a, %d %b %Y %H:%M:%S CST", time.localtime(t))
    for k, v in newslist.items():
        item = {"title": v[0], 
                'link': k, 
                'description': v[0], 
                'pubDate': mkpubDate(v[1]),
                'guid': k}
        channel.appendChild(genRSSItem(doc, item))
    global scie_rss
    scie_rss = doc.toxml('utf-8')
    return scie_rss

def genRSSItem(doc,  d, tag = 'item'):
    item = doc.createElement(tag)
    for k, v in d.items():
        kk = doc.createElement(k)
        vv = doc.createTextNode(v)
        kk.appendChild(vv)
        item.appendChild(kk)
    return item

def init():
    update_scie_news()

if 'SERVER_SOFTWARE' in os.environ:
    from bae.core.wsgi import WSGIApplication
    init()
    application = WSGIApplication(app)
elif __name__ == '__main__':
    init()
    app.run(host="0.0.0.0", debug=True)
    
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

from config import  scie, ee

scie_rss = "Hello"
ee_rss = "hello"

@app.route('/')
def root():
    return "Welcome!!\n"

@app.route('/<path>')
def other(path):
    return "can not find: " + path

@app.route('/get-scie-news.rss')
def rss_scie_news():
    global scie_rss
    return scie_rss

@app.route('/get-ee-news.rss')
def rss_ee_news():
    global ee_rss
    return ee_rss

@app.route('/update-all-news.cmd')
def update_all_news():
    update_scie_news()
    update_ee_news()
    
    return "Updated! at " + time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())


def update_scie_news(watch_days = 3*24*60*60, newslist = {}):
    url = scie['url']
    url_header = scie['url_header']
    pages = scie['pages']

    now = time.time()
    mktime = lambda x:time.mktime(time.strptime(x, "%Y-%m-%d %H:%M"))    
    
    for k in newslist:
        if newslist[k][1] + watch_days < now:
            del newslist[k]

    for page in pages:
        html = urllib2.urlopen(url_header+page).read()
        soup = BeautifulSoup(html)
        lilist = soup.find('ul', {'class':"newslist"}).findAll('li')
        for li in lilist:
            href = url + li.a['href']
            #utf-8
            the_time = mktime(li.span.text)
            if the_time + watch_days > now:
                newslist[href] = (li.a.text, the_time)
                
    global scie_rss
    scie_rss = gen_rss(scie['channel_info'], newslist)
    return scie_rss

def update_ee_news(watch_days = 3*24*60*60, newslist = {}):
    url = ee['url']
    url_header = ee['url_header']
    pages = ee['pages']

    now = time.time()
    mktime = lambda x:time.mktime(time.strptime(x, "%Y-%m-%d %H:%M:%S"))

    for k in newslist:
        if newslist[k][1] + watch_days < now:
            del newslist[k]

    for page in pages:
        html = urllib2.urlopen(url_header+page).read()
        soup = BeautifulSoup(html)
        lilist = soup.findAll('ul')[1].findAll('li')
        for li in lilist:
            href = url_header + li.a['href']
            #utf-8
            the_time = mktime(li.findAll('span')[1].text)
            if the_time + watch_days > now:
                newslist[href] = (li.a.text, the_time)

    global ee_rss
    ee_rss = gen_rss(ee['channel_info'], newslist)
    return ee_rss

#generate the rss xml string from newslist
def gen_rss(channel_info, newslist):
    doc = minidom.Document()
    rss = doc.createElement('rss')
    rss.setAttribute('version', '2.0')
    doc.appendChild(rss)
    
    channel = gen_rss_item(doc, channel_info, tag='channel')
    rss.appendChild(channel)

    mkpubDate = lambda t: time.strftime("%a, %d %b %Y %H:%M:%S CST", time.localtime(t))
    for k, v in newslist.items():
        item = {"title": v[0], 
                'link': k, 
                'description': v[0], 
                'pubDate': mkpubDate(v[1]),
                'guid': k}
        channel.appendChild(gen_rss_item(doc, item))
    return doc.toprettyxml(encoding='utf-8')

def gen_rss_item(doc,  d, tag = 'item'):
    item = doc.createElement(tag)
    for k, v in d.items():
        kk = doc.createElement(k)
        vv = doc.createTextNode(v)
        kk.appendChild(vv)
        item.appendChild(kk)
    return item

def init():
    update_all_news()

if 'SERVER_SOFTWARE' in os.environ:
    from bae.core.wsgi import WSGIApplication
    init()
    application = WSGIApplication(app)
elif __name__ == '__main__':
    init()
    app.run(host="0.0.0.0", debug=True)
    

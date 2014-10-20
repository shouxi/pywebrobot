#-*- coding:utf-8 -*-
#!/usr/bin/env python3
#from __future__ import print_function

import time
import os
import sys

if sys.version_info < (3, 0):
    import urllib2
    from HTMLParser import HTMLParser
else:
    import urllib.request as urllib2
    from html.parser import HTMLParser

from xml.dom import minidom

from rssconfig import scie, ee, scie_tmp_file, ee_tmp_file


def getroot():
    return os.path.join(os.environ.get('OPENSHIFT_REPO_DIR', './'), 'rss')
    #return os.path.join(os.environ.get('TMPDIR', './'), fn)


def outfile(fn, s):
    fn = os.path.join(getroot(), fn)
    with open(fn, 'w') as f:
        print(s, file=f)


class SCIEHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.newsitems = []

        self.in_newslist = None
        self.in_newsitem = None
        self.item_a = None
        self.item_span = None
        self.item = [None, None, None]

    def handle_starttag(self, tag, attrs):
        #print "Encountered the beginning of a %s tag" % tag
        if "ul" == tag and len(attrs) > 0:
            if ('class', 'newslist') == attrs[0]:
                self.in_newslist = True
        elif self.in_newslist and "li" == tag:
            self.in_newsitem = True
            self.item = [None, None, None]
        elif self.in_newsitem:
            if 'a' == tag:
                self.item_a = True
                k, v = attrs[0]
                if 'href' == k:
                    self.item[0] = v
            elif 'span' == tag:
                self.item_span = True

    def handle_endtag(self, tag):
        if "ul" == tag:
            self.in_newslist = False
        elif "li" == tag:
            self.in_newsitem = False
        elif "a" == tag:
            self.item_a = False
        elif "span" == tag:
            self.item_span = False
        
    def handle_data(self, data):
        if self.item_a:
            self.item[1] = data
        elif self.item_span:
            self.item[2] = data
        if self.item[0] and self.item[1] and self.item[2]:
            self.newsitems.append(self.item)
            self.item = [None, None, None]



class EEHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.newsitems = []

        self.in_newslist = None
        self.in_newsitem = None
        self.item_a = None
        self.item_span = None
        self.item = [None, None, None]

    def handle_starttag(self, tag, attrs):
        #print "Encountered the beginning of a %s tag" % tag
        if "table" == tag and len(attrs) > 0:
            if ('class', 'article-list') == attrs[0]:
                self.in_newslist = True
        elif self.in_newslist and "tr" == tag:
            self.in_newsitem = True
            self.item = [None, None, None]
        elif self.in_newsitem:
            # ('class', 'title')
            # ('class', 'article-list-date')
            if 'a' == tag and 2 == len(attrs):
                if ('class', 'title') == attrs[1]:
                    self.item[0] = attrs[0][1]  # (href, xxx)
                    self.item_a = True
            elif 'span' == tag and 1 == len(attrs):
                if ('class', 'article-list-date') == attrs[0]:
                    self.item_span = True

    def handle_endtag(self, tag):
        if "ul" == tag:
            self.in_newslist = False
        elif "li" == tag:
            self.in_newsitem = False
        elif "a" == tag:
            self.item_a = False
        elif "span" == tag:
            self.item_span = False
        
    def handle_data(self, data):
        if self.item_a:
            self.item[1] = data
        elif self.item_span:
            self.item[2] = data
        if self.item[0] and self.item[1] and self.item[2]:
            self.newsitems.append(self.item)
            self.item = [None, None, None]


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


def update_scie_news(watch_days = 7*24*60*60, newslist = {}):
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
        hp = SCIEHTMLParser()
        hp.feed(html.decode('utf-8'))
        for href, text, timestr in hp.newsitems:
            the_time = mktime(timestr)
            if the_time + watch_days > now:
                newslist[url + href] = (text, the_time)     
    scie_rss = gen_rss(scie['channel_info'], newslist)
    outfile(scie_tmp_file, scie_rss.decode())


def update_ee_news(watch_days = 3*24*60*60, newslist = {}):
    url = ee['url']
    url_header = ee['url_header']
    pages = ee['pages']

    now = time.time()
    mktime = lambda x:time.mktime(time.strptime(x, "%Y-%m-%d"))

    for k in newslist:
        if newslist[k][1] + watch_days < now:
            del newslist[k]

    for page in pages:
        html = urllib2.urlopen(url_header + page).read()
        hp = EEHTMLParser()
        hp.feed(html.decode())
        #print(hp.newsitems)
        for href, text, timestr in hp.newsitems:
            the_time = mktime(timestr)
            if the_time + watch_days > now:
                newslist[url + href] = (text, the_time)
                
    ee_rss = gen_rss(ee['channel_info'], newslist)
    outfile(ee_tmp_file, ee_rss.decode())



def batch():
    update_scie_news()
    update_ee_news()
    now_time = time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime())
    outfile('time', now_time)

    

if __name__ == '__main__':
    batch()
    print('ok')


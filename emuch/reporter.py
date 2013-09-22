#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request, urllib.parse
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
import datetime
import json

def get_xml(url):
    r = urllib.request.urlopen(url)
    xml_str = r.read().decode('utf-8')
    return xml_str

#the news published on $date
def get_news(url, date):
    xml_str = get_xml(url)
    root = ET.fromstring(xml_str)
    news = []
    keys = ['title', 'link', 'description',
            'copyright', 'pubDate', 'comments']
    p = HTMLParser()
    for item in root[0].findall('item'):
        new = {key: item.find(key).text for key in keys}
        for k in new:
            if new[k] is None: new[k] = ''
            new[k] = p.unescape(new[k])
        #pubdate = time.mktime(time.strptime(new['pubDate'], "%Y-%m-%d %H:%M"))
        #if pubdate > date + 10:
        if date in new['pubDate']:
            news.append(new)
    return news

#短地址
def get_dwz(longurl):
    tool = 'http://dwz.cn/create.php'
    data = urllib.parse.urlencode({'url': longurl}).encode('utf-8')
    request = urllib.request.Request(tool)
    request.add_header("Content-Type","application/x-www-form-urlencoded;charset=utf-8")
    f = urllib.request.urlopen(request, data)
    buf = f.read().decode('utf-8')

    answer = json.loads(buf)
    
    return answer['tinyurl'] if answer['status'] is 0 else longurl
    

def news2str(news):
    keys = ['title', 'link', 'description',
            'copyright', 'pubDate', 'comments']
    news_str = []
    readmore = b'\xd4\xc4\xb6\xc1\xc8\xab\xce\xc4'.decode('gbk')#阅读全文
    for new in news:
        new_str = '[{}] [b]{}[/b]\n{}[url={}][b][{}][/b][/url]'.format(
            new['pubDate'], new['title'], new['description'], get_dwz(new['link']), readmore)
        news_str.append(new_str)
        #time.sleep(1)

    if 0 == len(news):
        return '', None 
        
    return '\n\n'.join(news_str), news[0]['title']

'''
msg = {}
msg['url'] = '/post.php?action=newthread&fid=6' #休闲灌水
msg['threadtype'] = '1' #交流贴
msg['typeid'] = '6' #他站转载
msg['subject'] = u'标题'.encode('gbk')
msg['body'] = u'正文'.encode('gbk')
msg['keyword'] = ''
'''
#每天凌晨0点发布，获取上一天的新闻
def get_sciencenet_news(url=None):
    note = b'\xd7\xaa\xd4\xd8\xd7\xd4\xbf\xc6\xd1\xa7\xcd\xf8'.decode('gbk') #u'转载自科学网'
    ps = '\n\n**{}**[url={}]{}[/url]'.format(note, get_dwz('http://news.sciencenet.cn/'), 'http://news.sciencenet.cn/')
    if url is None: url = 'http://www.sciencenet.cn/xml/news.aspx?news=0'
    
    msg = {}
    msg['url'] = '/post.php?action=newthread&fid=6' #休闲灌水
    msg['threadtype'] = '1' #交流贴
    msg['typeid'] = '6' #他站转载
    msg['keyword'] = ''

    date = str(datetime.date.today() - datetime.timedelta(days = 1))
    body, sub_title = news2str(get_news(url, date))

    if sub_title is None:
        return None
    
    body += ps

    title_h = b'\xc3\xbf\xc8\xd5\xd0\xc2\xce\xc5'.decode('gbk') # u'每日新闻'
    title = '**{}**[{}~] {}'.format(title_h, date ,sub_title)
    
    msg['subject'] =  title.encode('gbk') 
    msg['body'] = body.encode('gbk')

    return msg

if '__main__' == __name__:
    long_url = 'http://www.sciencenet.cn/xml/news.aspx?di=0'
    print(get_dwz(long_url))
    url = 'http://www.sciencenet.cn/xml/news.aspx?di=1'
    msg = get_sciencenet_news(url)
    if msg is None:
        print('fucking')
    else:
        print(msg['subject'].decode('gbk'))
        print(msg['body'].decode('gbk'))
    

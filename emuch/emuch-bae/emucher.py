#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request, urllib.parse
import http.cookiejar
import time
import sched
import os, sys
import datetime

emuch_url = 'http://emuch.net/bbs'
user_agent = "Mozilla/5.0 (Windows NT 6.1; rv:23.0) Gecko/20100101 Firefox/23.0"

'''
username/passwd encoded as 'gbk'.
'''
def login_emuch(opener, username, passwd):
    url = emuch_url + '/logging.php?action=login'
    values = {'formhash': 'f6ac2e8a',
              'referer': 'http://emuch.net/bbs/index.php',
              'username': username,
              'password': passwd,
              'cookietime': '31536000',
              'loginsubmit': b'\xbb\xe1\xd4\xb1\xb5\xc7\xc2\xbc' #u'会员登录'.encode('gbk')
              }
    data = urllib.parse.urlencode(values)
    data = data.encode('utf-8')

    request = urllib.request.Request(url, data)#, method='POST')
    request.add_header("Content-Type","application/x-www-form-urlencoded;charset=utf-8")
    request.add_header('User-Agent', user_agent)

    r = opener.open(request)
    body = r.read().decode('gbk')
    #out_html(body, 'login')
    es = b'\xca\xe4\xc8\xeb\xb5\xc4\xd5\xca\xba\xc5\xc3\xdc\xc2\xeb\xb4\xed\xce\xf3\xa3\xac\xc7\xeb\xd6\xd8\xca\xd4'.decode('gbk')
    #输入的帐号密码错误，请重试

    f = es in body
    print_log({0: "logined successfully!", 1 :'error usename or password!'}[f])
    return not f

def get_msgbox(opener):
    url = emuch_url + '/box.php'
    request = urllib.request.Request(url)
    request.add_header("Content-Type","application/x-www-form-urlencoded;charset=utf-8")
    request.add_header('User-Agent', user_agent)

    return opener.open(request)

def get_credit(opener):
    url = emuch_url + '/memcp.php?action=getcredit'
    values = {'formhash': '2c8099cd',
              'getmode': '1', #2
              'message': '',
              'creditsubmit': b'\xc1\xec\xc8\xa1\xba\xec\xb0\xfc' #u'领取红包'.encode('gbk')
              }
    data = urllib.parse.urlencode(values)
    data = data.encode('utf-8')

    request = urllib.request.Request(url, data)#, method='POST')
    request.add_header("Content-Type","application/x-www-form-urlencoded;charset=utf-8")
    request.add_header('User-Agent', user_agent)

    print_log('try to get credit...')

    r = opener.open(request)
    body = r.read().decode('gbk')
    
    info = [b'\xb9\xa7\xcf\xb2\xa3\xa1\xc4\xe3\xbb\xf1\xb5\xc3'.decode('gbk'), #u'恭喜！你获得'
            b'\xbd\xf1\xcc\xec\xb5\xc4\xba\xec\xb0\xfc\xa3\xac\xc4\xfa\xd2\xd1\xbe\xad\xc1\xec\xc8\xa1\xc1\xcb\xa3\xac\xd2\xbb\xcc\xec\xbe\xcd\xd2\xbb\xb4\xce\xbb\xfa\xbb\xe1'.decode('gbk'),#u'今天的红包，您已经领取了，一天就一次机会'
            '',
            ]
    msgs = ['get credit successfully!', 'can not get twice!', 'undefined error!']
    #out_html(body, "get_credit")
    for i, s in enumerate(info):
        if s in body:
            print_log(msgs[i])
            return i

def enter_emuch(opener, login):
    s = b'\xb6\xd4\xb2\xbb\xc6\xf0\xa3\xac\xc4\xfa\xbb\xb9\xc3\xbb\xd3\xd0\xb5\xc7\xc2\xbc\xa3\xac\xce\xde\xb7\xa8\xbd\xf8\xd0\xd0\xb4\xcb\xb2\xd9\xd7\xf7'.decode('gbk')
    #u'对不起，您还没有登录，无法进行此操作'

    print_log('entering...')
    body = get_msgbox(opener).read().decode('gbk')
    f = (s not in body) or login()

    print_log({1: 'entered!', 0:''}[f])
    return f

def print_log(log, file = sys.stdout):
    print(time.strftime('%Y-%m-%d,%H:%M:%S  #  ',time.localtime(time.time())), log)

def out_html(s, filename = "out"):
    fp = open(filename + '.html', 'w')
    fp.write(s)
    fp.close()

def get_nettime():
    t_str = urllib.request.urlopen('http://www.baidu.com/').getheader('date')
    print(t_str)
    gmt = time.strptime(t_str[5:25], "%d %b %Y %H:%M:%S")
    return time.mktime(gmt)+8*60*60

def post_msg(opener, msg=None):
    if msg is None: return
    
    url = emuch_url + msg['url']
    values = {'formhash': 'a9f71df0',
              'threadtype': str(msg['threadtype']), #'1': 交流贴， '3':资源帖,
              'helpcredit': '0',
              'credit_give': '1',
              'credit_num': '0',
              'helpcredit2': '0',
              'tmp[]': '1',
              'salecredit': '1',
              'salenum': '10',
              'typeid': str(msg['typeid']), #'6':网络转载, '81':交流畅谈，'1255':硕博心情
              'subject': msg['subject'], #
              'mode': '2',
              'font': 'Verdana',
              'size': '3',
              'color': 'Black',
              'message': msg['body'],
              'keyword': msg['keyword'],
              'topicsubmit': b'\xc1\xa2\xbc\xb4\xb7\xa2\xb2\xbc'.decode('gbk')#立即发布
              }
    data = urllib.parse.urlencode(values)
    data = data.encode('utf-8')

    request = urllib.request.Request(url, data)#, method='POST')
    request.add_header("Content-Type","application/x-www-form-urlencoded;charset=utf-8")
    request.add_header('User-Agent', user_agent)

    print_log('post a message...')
    r = opener.open(request)

    body = r.read().decode('gbk')
    out_html(body, 'post')
    
    es = b'\xb6\xd4\xb2\xbb\xc6\xf0\xa3\xac\xc4\xfa\xd4\xda10\xb7\xd6\xd6\xd3\xc4\xda\xb2\xbb\xc4\xdc\xc1\xac\xd0\xf8\xb7\xa2\xb2\xbc\xb6\xe0\xb8\xf6\xd6\xf7\xcc\xe2\xc5\xb6'.decode('gbk')    
    #u'对不起，您在10分钟内不能连续发布多个主题哦'
    f = es in body
    if f: print_log('10 minutes limited!')
    
    return not f
    
    
if '__main__' == __name__:
    from config import username, passwd

    cj_file = "robot-emuch-cookies.txt"
    cj = http.cookiejar.MozillaCookieJar(cj_file)
    try:
        cj.load(ignore_discard=True, ignore_expires=True)
    except Exception:
        """create a cookie file"""
        cj.save(ignore_discard=True, ignore_expires=True)

    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    
    login = lambda : login_emuch(opener, username, passwd)
    enter = lambda : enter_emuch(opener, login)
    
    creditd = lambda : (not enter()) or get_credit(opener)
    cjsaved = lambda : cj.save(ignore_discard=True, ignore_expires=True)

    creditd()

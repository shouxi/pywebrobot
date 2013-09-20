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

    return opener.open(request)

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

    print_log('try get credit...')

    info = [b'\xb9\xa7\xcf\xb2\xa3\xa1\xc4\xe3\xbb\xf1\xb5\xc3'.decode('gbk'), #u'恭喜！你获得'
            b'\xbd\xf1\xcc\xec\xb5\xc4\xba\xec\xb0\xfc\xa3\xac\xc4\xfa\xd2\xd1\xbe\xad\xc1\xec\xc8\xa1\xc1\xcb\xa3\xac\xd2\xbb\xcc\xec\xbe\xcd\xd2\xbb\xb4\xce\xbb\xfa\xbb\xe1'.decode('gbk'),#u'今天的红包，您已经领取了，一天就一次机会'
            '',
            ]
    msgs = ['get credit successfully!', 'can not get twice!', 'undefined error!']
    r = opener.open(request)
    body = r.read().decode('gbk')
    #out_html(body, "get_credit")
    for i, s in enumerate(info):
        if s in body:
            print_log(msgs[i])
            return i

def enter_emuch(opener, username, passwd):
    s = b'\xb6\xd4\xb2\xbb\xc6\xf0\xa3\xac\xc4\xfa\xbb\xb9\xc3\xbb\xd3\xd0\xb5\xc7\xc2\xbc\xa3\xac\xce\xde\xb7\xa8\xbd\xf8\xd0\xd0\xb4\xcb\xb2\xd9\xd7\xf7'.decode('gbk')
    #u'对不起，您还没有登录，无法进行此操作'

    print_log('entering...')
    body = get_msgbox(opener).read().decode('gbk')
    if s in body:
        login_emuch(opener, username, passwd)
        print_log('logining...')

    time.sleep(2)

    body = get_msgbox(opener).read().decode('gbk')
    if s in body:
        print_log('login error!')
        return False
    else:
        print_log('entered!')
        return True

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

#demos
def get_creditd(scheduler, opener, login, handler = None):
    if not enter_emuch(opener, username, passwd): return
    get_credit(opener)

    tomorrow = datetime.date.today() + datetime.timedelta(days = 1)
    ttime = time.mktime(time.strptime(str(tomorrow), "%Y-%m-%d"))
    inc = int(ttime - time.time() + 5*60)
    #inc = 10
    print_log('wait {0} hours, {1} minutes, {2} seconds for next credit...'
              .format(inc//3600, (inc //60) %60, inc % 60))

    if handler is not None: handler()
    scheduler.enter(inc, 0, get_creditd, (scheduler, opener, login, handler))
                
def rebot(username, passwd):
    cj_file = "robot-emuch-cookies.txt"
    cj = http.cookiejar.MozillaCookieJar(cj_file)
    try:
        cj.load(ignore_discard=True, ignore_expires=True)
    except Exception:
        """create a cookie file"""
        cj.save(ignore_discard=True, ignore_expires=True)

    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    login = lambda : enter_emuch(opener, username, passwd)
    save_cj = lambda : cj.save(ignore_discard=True, ignore_expires=True)

    scheduler = sched.scheduler(time.time, time.sleep)

    scheduler.enter(10, 0, get_creditd, (scheduler, opener, login, save_cj))

    scheduler.run()

if '__main__' == __name__:
    from config import username, passwd
    rebot(username, passwd)
    

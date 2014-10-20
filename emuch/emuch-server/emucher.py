#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request
import urllib.parse
import http.cookiejar
import time
import sched
import os
import sys
import datetime
import inspect

'''
username/passwd encoded as 'gbk'.
'''

emuch_url = 'http://emuch.net/bbs'
user_agent = "Mozilla/5.0 (Windows NT 6.1; rv:23.0) Gecko/20100101 Firefox/23.0"

def mk_request(url, values=None):
    data = None
    if values is not None:
        data = urllib.parse.urlencode(values)
        data = data.encode('utf-8')

    request = urllib.request.Request(url, data)#, method='POST')
    request.add_header("Content-Type", "application/x-www-form-urlencoded;charset=utf-8")
    request.add_header('User-Agent', user_agent)
    return request


def login_emuch(opener, username, passwd, logger):
    url = emuch_url + '/logging.php?action=login'
    values = {'formhash': 'f6ac2e8a',
              'referer': 'http://emuch.net/bbs/index.php',
              'username': username,
              'password': passwd,
              'cookietime': '31536000',
              'loginsubmit': b'\xbb\xe1\xd4\xb1\xb5\xc7\xc2\xbc' #u'会员登录'.encode('gbk')
              }

    r = opener.open(mk_request(url, values))
    body = r.read().decode('gbk')
    sec_code, sec_code_hash = get_CAPTCHA(body)
    time.sleep(5)

    values = {'formhash': '412107bd',
              'username': username,
              'post_sec_code': sec_code,
              'post_sec_hash': sec_code_hash,
              'loginsubmit': b'\xcc\xe1\xbd\xbb'  #u'提交'.encode('gbk')
              }

    r = opener.open(mk_request(url, values))
    body = r.read().decode('gbk')

    #out_html(body, 'login')
    es = u'输入的帐号密码错误，请重试'
    f = es in body
    logger({0: "logined successfully!", 1 :'error usename or password!'}[f])
    return not f

def get_CAPTCHA(body):
    s1 = u'问题：'
    s2 = u'等于多少?'
    s3 = u'<input type="hidden" name="post_sec_hash" value="'
    s4 = u'">'
    calc = {
        u'乘以': lambda x, y: x * y,
        u'除以': lambda x, y: x // y,
        u'加上': lambda x, y: x + y,
        u'减去': lambda x, y: x - y
    }
    i = body.find(s3)
    i += len(s3)
    j = body[i:].find(s4)
    sec_code_post = body[i: i+j]

    i = body.find(s1)
    if i is -1:
        return 0
    i += len(s1)
    j = body[i:].find(s2)
    exprstr = body[i: i+j]
    for k, v in calc.items():
        i = exprstr.find(k)
        if i != -1:
            j = i + len(k)
            x = int(exprstr[:i])
            y = int(exprstr[j:])
            return str(v(x, y)), sec_code_post
    return '#Cannot getVerification code...'


def get_msgbox(opener):
    time.sleep(5)
    url = emuch_url + '/box.php'
    return opener.open(mk_request(url))

def get_credit(opener, logger):
    url = emuch_url + '/memcp.php?action=getcredit'
    values = {'formhash': '2c8099cd',
              'getmode': '1', #2
              'message': '',
              'creditsubmit': b'\xc1\xec\xc8\xa1\xba\xec\xb0\xfc' #u'领取红包'.encode('gbk')
              }

    time.sleep(5)
    logger('try to get credit...')

    r = opener.open(mk_request(url, values))
    body = r.read().decode('gbk')
    
    info = [u'恭喜！你获得',
            u'今天的红包，您已经领取了，一天就一次机会',
            '',
            ]
    msgs = ['get credit successfully!', 'can not get twice!', 'undefined error!']
    #out_html(body, "get_credit")
    for i, s in enumerate(info):
        if s in body:
            logger(msgs[i])
            return i

def enter_emuch(opener, login, logger):
    s = u'对不起，您还没有登录，无法进行此操作'

    logger('entering...')
    body = get_msgbox(opener).read().decode('gbk')
    f = (s not in body) or login()

    logger({1: 'entered!', 0:''}[f])
    return f


def out_html(s, filename="out"):
    fp = open(filename + '.html', 'w')
    fp.write(s)
    fp.close()


def get_nettime():
    t_str = urllib.request.urlopen('http://www.baidu.com/').getheader('date')
    gmt = time.strptime(t_str[5:25], "%d %b %Y %H:%M:%S")
    return time.mktime(gmt)+8*60*60


def mk_tasks(username, passwd, logger):
    cj_file = "{0}-emuch-cookies.txt".format(sum(username))
    cj = http.cookiejar.MozillaCookieJar(cj_file)
    try:
        cj.load(ignore_discard=True, ignore_expires=True)
    except Exception:
        """create a cookie file"""
        cj.save(ignore_discard=True, ignore_expires=True)

    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

    login = lambda: login_emuch(opener, username, passwd, logger)
    enter = lambda: enter_emuch(opener, login, logger)
    creditd = lambda: (not enter()) or get_credit(opener, logger)
    cjsaved = lambda: cj.save(ignore_discard=True, ignore_expires=True)

    return [creditd, cjsaved]


def debug_log(log, file=sys.stdout):
    msg = time.strftime('%Y-%m-%d,%H:%M:%S  #  ',time.localtime(time.time())) + log
    print(msg, file=file)


if '__main__' == __name__:
    from config import users
    tasks = []
    for k, v in users.items():
        vv = mk_tasks(k, v, logger=debug_log)
        tasks.extend(vv)
    for t in tasks:
        t()



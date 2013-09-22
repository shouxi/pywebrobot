#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request, urllib.parse
import http.cookiejar
import time
import sched
import datetime

from reporter import get_sciencenet_news
from emucher import *

#demos
#handler
#每天凌晨0点重复执行

def call_daily(scheduler, lst = []):
    for func in lst:
        func()
        time.sleep(1)
        
    tomorrow = datetime.date.today() + datetime.timedelta(days = 1)
    nexttime = time.mktime(time.strptime(str(tomorrow), "%Y-%m-%d"))
    inc = int(nexttime - time.time() + 3*60)
    
    print_log('wait {0} hours, {1} minutes, {2} seconds for next calling...'
              .format(inc//3600, (inc //60) %60, inc % 60))

    scheduler.enter(inc, 0, call_daily, (scheduler, lst))
    
def rebot(username, passwd):
    rss_url = 'http://www.sciencenet.cn/xml/paper.aspx?di=0'
    #rss_url = 'http://www.sciencenet.cn/xml/news.aspx?news=0'
    
    
    cj_file = "robot-emuch-cookies.txt"
    cj = http.cookiejar.MozillaCookieJar(cj_file)
    try:
        cj.load(ignore_discard=True, ignore_expires=True)
    except Exception:
        """create a cookie file"""
        cj.save(ignore_discard=True, ignore_expires=True)

    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    poster = lambda msg: post_msg(opener, msg)

    login = lambda : login_emuch(opener, username, passwd)
    enter = lambda : enter_emuch(opener, login)
    msger = lambda: get_sciencenet_news(rss_url)

    creditd = lambda : (not enter()) or get_credit(opener)
    newserd = lambda : (not enter()) or poster(msger())
    cjsaved = lambda : cj.save(ignore_discard=True, ignore_expires=True)

    jobs = [creditd, newserd, cjsaved]

    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler.enter(1, 0, call_daily, (scheduler, jobs))
    scheduler.run()
    
if '__main__' == __name__:
    from config import username, passwd
    rebot(username, passwd)

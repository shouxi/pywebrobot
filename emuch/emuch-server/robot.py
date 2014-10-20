#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import sched
import datetime
import inspect
import os

from emucher import mk_tasks

#demos
#handler
#每天凌晨0点重复执行

def call_daily(scheduler, lst=[]):
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    nexttime = time.mktime(time.strptime(str(tomorrow), "%Y-%m-%d"))
    i = 0
    while i < 5:
        try:
            for func in lst:
                func()
                time.sleep(2)
            i = 6
            break
        except:
            i = i + 1
            print('except')

    inc = int(nexttime - time.time() + 3*60)

    logger('wait {0} hours, {1} minutes, {2} seconds for next calling...'.format(
         inc//3600, (inc//60) % 60, inc % 60))
    logger()

    scheduler.enter(inc, 0, call_daily, (scheduler, lst))


def logger(log=None, msgs=[]):
    msg = time.strftime('%Y-%m-%d,%H:%M:%S  # ',time.localtime(time.time())) + str(log)
    print(msg)
    msgs.append(msg)

    if log is None:
        #caller_file = inspect.stack()[1][1]         # caller's filename
        #path = os.path.abspath(os.path.dirname(caller_file))
        #log_file = os.path.join(os.path.dirname(path), 'logs.txt')
        log_file = 'logs.txt'
        with open(log_file, 'w') as fp:
            for msg in msgs:
                print(msg, file=fp)
        msgs.clear()

def rebot(users):
    tasks = []
    for n, p in users.items():
        tasks.extend(mk_tasks(n, p, logger))

    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler.enter(1, 0, call_daily, (scheduler, tasks))
    scheduler.run()

if '__main__' == __name__:
    from config import users
    rebot(users)
    


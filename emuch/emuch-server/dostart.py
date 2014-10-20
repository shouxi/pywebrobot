#! /usr/bin/env python

import os
uid = user_uid
script_path = 'script-path'
start_cmd = 'nohup /usr/bin/python3 robot.py > coin.log 2>&1 &'
ouid = os.getuid()
os.seteuid(uid)
os.chdir(script_path)
os.system(start_cmd)
#os.system('exit')
os.seteuid(ouid)


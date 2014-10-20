#-*- coding:utf-8 -*-
#!/usr/bin/env python

import os
from bottle import Bottle, run, static_file
from rssconfig import scie_tmp_file, ee_tmp_file
from genrss import batch, getroot


app = Bottle()


@app.route('/')
def root():
    return "Welcome!!\n"


# scie-news
# ee-news
# time
@app.route('/rss/<filename>')
def getrss(filename):
	return static_file(filename, root=getroot())

@app.route('/rss/path')
def getrss():
	return getroot()

@app.error(404)
def mistake(code):
    return 'Get You!'


application = app


if __name__ == '__main__':
    run(app=app, host='localhost', port=8088, debug=True)

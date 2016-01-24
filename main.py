#!/usr/bin/env python
#-*- coding: utf-8 -*-

import re
import os
import sys
import time
import urllib2
import contextlib
import getopt
from threading import Timer


# 保存content中的内容到本地root/dirname/filename中，并把原来的路径url替换为本地路径
def save_and_replace(html, dirname, filename, content, url, root):
    if not os.path.isdir(root + dirname + '/'):
        os.mkdir(root + dirname + '/')
    with open(root + dirname + '/' + filename, 'wb') as f:
        f.write(content)

    return html.replace(url, dirname + '/' + filename, 1)

# 获取html中的外链Css内容并save_and_replace，同时要对Css中的图片进行路径更换
def get_css(html, root):
    try:
        ms = re.finditer(r'type="text/css" href="(.*?)"', html)  #查找外链Css
        if ms:
            for m in ms:
                css_url = m.group(1)
                with contextlib.closing(urllib2.urlopen(css_url)) as u:
                    css = u.read()
                css_name = css_url.split('/')[-1]

                mms = re.finditer(r'url\(\.\./\.\./(.*?)\)', css)  #查找Css中的图片
                if mms:
                    for mm in mms:
                        url_parts = css_url.rstrip('\n').split('/')
                        relative_url = '/'.join(s for s in url_parts[:len(url_parts)-3])
                        img_url = relative_url + '/' + mm.group(1)
                        original_url = '../../' + mm.group(1)
                        css = css.replace(original_url, img_url, 1)
                html = save_and_replace(html, 'css', css_name, css, css_url, root)

        return html
    except urllib2.HTTPError as e:
        print e.code

# 获取html中的图片并save_and_replace
def get_img(html, root_url, root):
    try:
        ms = re.finditer(r'<img src="(.*?)"', html)  #路径为格式一的图片
        if ms:
            for m in ms:
                img_url = m.group(1)
                with contextlib.closing(urllib2.urlopen(img_url)) as u:
                    img = u.read()
                img_name = img_url.split('/')[-1]
                if img_name == 'imgloading.jpg':
                    continue
                html = save_and_replace(html, 'images', img_name, img, img_url, root)

        ms = re.finditer(r'<img src="(.*?)" original="(.*?)"', html)  #路径为格式二的图片
        if ms:
            for m in ms:
                img_url = m.group(2)
                with contextlib.closing(urllib2.urlopen(img_url)) as u:
                    img = u.read()
                img_name = img_url.split('/')[-1]
                html = save_and_replace(html, 'images', img_name, img, m.group(1), root)

        ms = re.finditer(r'href="/images/(.*?)"', html)  #路径为格式三的图片
        if ms:
            for m in ms:
                img_name = m.group(1)
                original_url = '/images/' + img_name
                img_url = root_url + original_url
                with contextlib.closing(urllib2.urlopen(img_url)) as u:
                    img = u.read()
                html = save_and_replace(html, 'images', img_name, img, original_url, root)

        return html
    except urllib2.HTTPError as e:
        print e.code

# 获取html中的外链JS并save_and_replace
def get_js(html, root):
    try:
        ms = re.finditer(r'type="text/javascript" src="(.*?)"', html)
        if ms:
            for m in ms:
                js_url = m.group(1)
                with contextlib.closing(urllib2.urlopen(js_url)) as u:
                    js = u.read()
                js_name = js_url.split('/')[-1]
                html = save_and_replace(html, 'js', js_name, js, js_url, root)

        return html
    except urllib2.HTTPError as e:
        print e.code

# 把html中的相对于http://m.sohu.com的相对路径替换为绝对路径
def change_relative_url(html, root_url):
    ms = re.finditer(r'href="/(.*?)"', html)
    if ms:
        for m in ms:
            if len(m.group(1)) == 0:
                continue
            html = html.replace('/' + m.group(1), root_url + '/' + m.group(1), 1)

    return html

# 利用getopt模块获取命令行参数
def get_args():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'd:u:o:')
    except getopt.GetoptError:
        print 'getopt error!'
    
    d = ''
    url = ''
    oriention = ''
    for op, value in opts:
        if op == '-d':
            d = value
        elif op == '-u':
            url = value
        elif op == '-o':
            oriention = value
    if not (d and url and oriention):
        print 'lack arguments!'
        sys.exit(1)
    return url, d, oriention

# 主运行函数
def main(url, oriention):
    print time.time()
    t = time.strftime("%Y%m%d%H%M", time.localtime(time.time()))
    if not os.path.isdir(oriention + '/' + t):
        os.makedirs(oriention + '/' + t)
    root = oriention + '/' + t + '/'
    html = urllib2.urlopen(url).read()
    print 'getting css...'
    html = get_css(html, root)
    print 'getting img...'
    html = get_img(html, url, root)
    print 'getting js...'
    html = get_js(html, root)
    html = change_relative_url(html, url)
    print 'writing html'
    with open(root + 'index.html', 'w') as f:
        f.write(html)


if __name__ == '__main__':
    # 获取参数
    url, d, oriention = get_args()
    # 先立即备份一次
    Timer(0, main, [url, oriention]).start()
    # 再每隔60s备份一次
    while True:
        Timer(int(d), main, [url, oriention]).start()
        time.sleep(int(d))

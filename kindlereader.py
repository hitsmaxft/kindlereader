#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
main.py
Created by Jerry<lxb429@gmail.com> on 2010-11-08.
"""

__author__  = "Jerry<lxb429@gmail.com>"
__version__ = "0.3"

import sys
import os
import time
import hashlib
import re
import uuid
import string
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import parsedate_tz
from lib import smtplib
import codecs
import ConfigParser
import getpass
import subprocess

from lib.libgreader import *
from lib.tornado import template
from lib.tornado import escape
from lib.BeautifulSoup import BeautifulSoup

import socket, urllib2, urllib
socket.setdefaulttimeout(20)

iswindows = 'win32' in sys.platform.lower() or 'win64' in sys.platform.lower()
isosx     = 'darwin' in sys.platform.lower()
isfreebsd = 'freebsd' in sys.platform.lower()
islinux   = not(iswindows or isosx or isfreebsd)

TEMPLATES = {}
TEMPLATES['content.html'] = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"> 
    <title>{{ user['userName'] }}'s google reader</title>
    <style type="text/css">
    body{
        font-size: 1.1em;
        margin:0 5px;
    }

    h1{
        font-size:4em;
        font-weight:bold;
    }

    h2 {
        font-size: 1.2em;
        font-weight: bold;
        margin:0;
    }
    a {
        color: inherit;
        text-decoration: inherit;
        cursor: default
    }
    a[href] {
        color: blue;
        text-decoration: underline;
        cursor: pointer
    }
    p{
        text-indent:1.5em;
        line-height:1.3em;
        margin-top:0;
        margin-bottom:0;
    }
    .italic {
        font-style: italic
    }
    .do_article_title{
        line-height:1.5em;
        page-break-before: always;
    }
    #cover{
        text-align:center;
    }
    #toc{
        page-break-before: always;
    }
    #content{
        margin-top:10px;
        page-break-after: always;
    }
    </style>
</head>
<body>
    <div id="cover">
        <h1 id="title">{{ user['userName'] }}'s Google reader</h1>
        <a href="#content">Go straight to first item</a><br />
        {{ datetime.datetime.now().strftime("%m/%d %H:%M") }}
    </div>
    <div id="toc">
        <h2>Feeds:</h2> 
        <ol> 
            {% set feed_count = 0 %}
            {% for feed in feeds %}
            
            {% if feed.item_count > 0 %}
            {% set feed_count = feed_count + 1 %}
            <li>
              <a href="#sectionlist_{{ feed.idx }}">{{ feed.title }}</a>
              <br />
              {{ feed.item_count }} items
            </li>
            {% end %}

            {% end %}
        </ol> 
          
        {% for feed in feeds %}
        {% if feed.item_count > 0 %}
        <mbp:pagebreak></mbp:pagebreak>
        <div id="sectionlist_{{ feed.idx }}" class="section">
            {% if feed.idx < feed_count %}
            <a href="#sectionlist_{{ feed.idx+1 }}">Next Feed</a> |
            {% end %}
            
            {% if feed.idx > 1 %}
            <a href="#sectionlist_{{ feed.idx-1 }}">Previous Feed</a> |
            {% end %}
        
            <a href="#toc">TOC</a> |
            {{ feed.idx }}/{{ feed_count }} |
            {{ feed.item_count }} items
            <br />
            <h3>{{ feed.title }}</h3>
            <ol>
                {% for item in feed.items %}
                <li>
                  <a href="#article_{{ feed.idx }}_{{ item.idx }}">{{ item.title }}</a><br/>
                  {% if item.published %}{{ item.published }}{% end %}
                </li>
                {% end %}
            </ol>
        </div>
        {% end %}
        {% end %}
    </div>
    <mbp:pagebreak></mbp:pagebreak>
    <div id="content">
        {% for feed in feeds %}
        {% if feed.item_count > 0 %}
        <div id="section_{{ feed.idx }}" class="section">
        {% for item in feed.items %}
        <div id="article_{{ feed.idx }}_{{ item.idx }}" class="article">
            <h2 class="do_article_title">
              {% if item.url %}
              <a href="{{ item.url }}">{{ item.title }}</a>
              {% else %}
              {{ item.title }}
              {% end %}
            </h2>
            {% if item.published %}{{ item.published }}{% end %}
            <div>{{ item.content }}</div>
        </div>
        {% end %}
        </div>
        {% end %}
        {% end %}
    </div>
</body>
</html>
"""

TEMPLATES['book.html'] = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
<head>
<title>{{ user['userName'] }}'s google reader</title>
<meta http-equiv="content-type" content="text/html; charset=UTF-8"/>
<style type="text/css">
body{
    margin:5px;
    font-size: 1.2em;
}
</style>
<guide>
    <reference type="start" title="start" href="#content"></reference>
    <reference type="toc" title="toc" href="#toc"></reference>
    <reference type="text" title="cover" href="#cover"></reference>
</guide>
</head>
<body>
  <div id="cover">
    <h1>{{ user['userName'] }}'s Google reader</h1>
    <ul>
        <li><a href="#content">Go straight to first item</a></li>
    </ul>
    <p>Date:{{ datetime.datetime.now().strftime("%m/%d %H:%M") }}</p>
  </div>
  <mbp:pagebreak></mbp:pagebreak>

  <div id="toc">
    <div id="feeds">
        {% set feed_count = 0 %}
        <h2>Feeds:</h2>
        <ol>
            {% for feed in feeds %}
            {% if feed.item_count > 0 %}
            {% set feed_count = feed_count + 1 %}
            <li>
                <a href="#feed-{{ feed.idx }}">{{ feed.title }}</a>
                <br> 
                {{ feed.item_count }} items
            </li>
            {% end %}
            {% end %}
        </ol>
    </div>
    <mbp:pagebreak></mbp:pagebreak>
    
    {% for feed in feeds %}
    {% if feed.item_count > 0 %}
    <div id="feed-{{ feed.idx }}">
        <div>
            {% if feed.idx < feed_count %}
            <a href="#feed-{{ feed.idx+1 }}">Next Feed</a> |
            {% end %}
            
            {% if feed.idx > 1 %}
            <a href="#feed-{{ feed.idx-1 }}">Previous Feed</a> |
            {% end %}
        
            <a href="#toc">TOC</a> |
            {{ feed.idx }}/{{ feed_count }} |
            {{ feed.item_count }} items
        </div>
        <h3><a href="#feed-content-{{ feed.idx }}">{{ feed.title }}</a></h3>
        <ol>
            {% for item in feed.items %}
            <li>
              <a href="#item-{{ feed.idx }}.{{ item.idx }}">{{ item.title }}</a>
              {% if item.published %}<br/>{{ item.published }}{% end %}
            </li>
            {% end %}
        </ol>
    </div>
    {% end %}
    {% end %}
  
  </div><!-- end toc -->
  <mbp:pagebreak></mbp:pagebreak>

  <div id="content">
  {% for feed in feeds %}
  {% if feed.item_count > 0 %}
  <div id="feed-content-{{ feed.idx }}">
    <h2>{{ feed.title }}</h2>
    {% for item in feed.items %}
    <div id="item-{{ feed.idx }}.{{ item.idx }}">
        <h3>
            {% if item.url %}
            <a href="{{ item.url }}">{{ item.title }}</a>
            {% else %}
            {{ item.title }}
            {% end %}
        </h3>
        <div>
            {% if item.idx < feed.item_count %}
            <a href="#item-{{ feed.idx }}.{{ item.idx+1 }}">Next</a> |
            {% elif feed.idx < feed_count %}
            <a href="#feed-content-{{ feed.idx+1 }}">Next Feed</a> |
            {% end %}
            
            <a href="#feed-{{ feed.idx }}">{{ feed.title[:5] }}...</a> |
            <a href="#toc">TOC</a> |
            {% if item.published %}{{ item.published }} |{% end %}
            {{ item.idx }}/{{ feed.item_count }}
        </div>
        <div>
            {{ item.content }}
        </div>
        {% end %}
    </div>
  </div>
  {% end %}
  {% end %}
  </div>
</body>
</html>
"""

TEMPLATES['toc.ncx'] = """<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1" xml:lang="zh-CN">
<head>
<meta name="dtb:uid" content="{{ user['userId'] }}" />
<meta name="dtb:depth" content="4" />
<meta name="dtb:totalPageCount" content="0" />
<meta name="dtb:maxPageNumber" content="0" />
</head>
<docTitle><text>{{ user['userName'] }}'s Google reader</text></docTitle>
<docAuthor><text>{{ user['userName'] }}</text></docAuthor>
<navMap>
    {% if format == 1 %}
    <navPoint class="periodical">
        <navLabel><text>{{ user['userName'] }}'s Google reader</text></navLabel>
        <content src="content.html" />
        {% for feed in feeds %}
        {% if feed.item_count > 0 %}
        <navPoint class="section" id="{{ feed.idx }}">
            <navLabel><text>{{ escape(feed.title) }}</text></navLabel>
            <content src="content.html#section_{{ feed.idx }}" />
            {% for item in feed.items %}
            <navPoint class="article" id="{{ feed.idx }}_{{ item.idx }}" playOrder="{{ item.idx }}">
              <navLabel><text>{{ escape(item.title) }}</text></navLabel>
              <content src="content.html#article_{{ feed.idx }}_{{ item.idx }}" />
            </navPoint>
            {% end %}
        </navPoint>
        {% end %}
        {% end %}
    </navPoint>
    {% else %}
    <navPoint class="book">
        <navLabel><text>{{ user['userName'] }}'s Google reader</text></navLabel>
        <content src="content.html" />
        {% for feed in feeds %}
        {% if feed.item_count > 0 %}
            {% for item in feed.items %}
            <navPoint class="chapter" id="{{ feed.idx }}_{{ item.idx }}" playOrder="{{ item.idx }}">
                <navLabel><text>{{ escape(item.title) }}</text></navLabel>
                <content src="content.html#article_{{ feed.idx }}_{{ item.idx }}" />
            </navPoint>
            {% end %}
        {% end %}
        {% end %}
    </navPoint>
    {% end %}
</navMap>
</ncx>
"""

TEMPLATES['content.opf']= """<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="2.0" unique-identifier="uid">
<metadata>
<dc-metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
    <dc:title>{{ user['userName'] }}'s Google reader({{ datetime.datetime.now().strftime("%m/%d %H:%M") }})</dc:title>
    <dc:language>zh-CN</dc:language>
    <dc:identifier id="uid">{{ user['userId'] }}{{ datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ") }}</dc:identifier>
    <dc:creator>kindlereader</dc:creator>
    <dc:publisher>kindlereader</dc:publisher>
    <dc:subject>{{ user['userName'] }}'s Google reader</dc:subject>
    <dc:date>{{ datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ") }}</dc:date>
    <dc:description></dc:description>
</dc-metadata>
{% if format == 1 %}
<x-metadata>
    <output encoding="utf-8" content-type="application/x-mobipocket-subscription-magazine"></output>
    </output>
</x-metadata>
{% end %}
</metadata>
<manifest>
    <item id="content" media-type="application/xhtml+xml" href="content.html"></item>
    <item id="toc" media-type="application/x-dtbncx+xml" href="toc.ncx"></item>
</manifest>

<spine toc="toc">
    <itemref idref="content"/>
</spine>

<guide>
    <reference type="start" title="start" href="content.html#content"></reference>
    <reference type="toc" title="toc" href="content.html#toc"></reference>
    <reference type="text" title="cover" href="content.html#cover"></reference>
</guide>
</package>
"""

def find_kindlegen_prog():
    kindlegen_prog = 'kindlegen' + (iswindows and '.exe' or '')

    # search in current directory and PATH to find kinglegen
    sep = iswindows and ';' or ':'
    dirs = ['.']
    dirs.extend(os.getenv('PATH').split(sep))
    for dir in dirs:
        if dir:
            fname = os.path.join(dir, kindlegen_prog)
            if os.path.exists(fname):
                # print fname
                return fname

kindlegen = find_kindlegen_prog()

class KindleReader(object):
    """docstring for KindleReader"""
    
    work_dir = None
    config = None
    template_file = None
    password = None
    
    remove_tags = ['script', 'object','video','embed','iframe','noscript']
    remove_attributes = ['class','id','title','style','width','height','onclick']
    max_image_number = 0
    user_agent = "kindlereader/0.2"
    
    def __init__(self, work_dir=None, conf_file=None, template_file=None):

        if work_dir:
            self.work_dir = work_dir
        else:
            self.work_dir = os.path.dirname(sys.argv[0])

        if conf_file is None:
            conf_file = os.path.join(self.work_dir, "config.ini")

        if os.path.isfile(conf_file) is False:
            raise Exception("config file '%s' not found" % conf_file)
        
        self.config = ConfigParser.ConfigParser()
        
        if iswindows:
            self.config.readfp(codecs.open(conf_file, "r", "utf-8-sig"))
        else:
            self.config.readfp(codecs.open(conf_file, "r", "utf-8"))

        if template_file is not None and os.path.isfile(template_file) is False:
            raise Exception("template file '%s' not found" % template_file)
        else:
            self.template_file = template_file

        self.password =  self.get_config('reader', 'password')
        if not self.password:
            self.password = getpass.getpass("please input your google reader's password:")
            
    def get_config(self, section, name):
        
        try:
            return self.config.get(section, name).strip()
        except:
            return None
      
    def sendmail(self, data, file_type='html'):
        """send html to kindle"""
    
        mail_host = self.get_config('mail', 'host')
        mail_port = self.get_config('mail', 'port')
        mail_ssl = self.get_config('mail', 'ssl')
        mail_from = self.get_config('mail', 'from')
        mail_to = self.get_config('mail', 'to')
        mail_username = self.get_config('mail', 'username')
        mail_password = self.get_config('mail', 'password')
        
        if not mail_from:
            raise Exception("'mail from' is empty")
        
        if not mail_to:
            raise Exception("'mail to' is empty")
        
        if not mail_host:
            raise Exception("'mail host' is empty")
            
        if not mail_port:
            mail_port = 25
            
        print "send mail to %s ... " % mail_to,
    
        msg = MIMEMultipart()
        msg['from'] = mail_from
        msg['to'] = mail_to
        msg['subject'] = 'Convert'
    
        htmlText = 'google reader delivery.'
        msg.preamble = htmlText
    
        msgText = MIMEText(htmlText, 'html', 'utf-8')  
        msg.attach(msgText)  
    
        att = MIMEText(data, 'base64', 'utf-8')
        att["Content-Type"] = 'application/octet-stream'
        att["Content-Disposition"] = 'attachment; filename="google-reader-%s.%s"' % (time.strftime('%H-%M-%S'), file_type)
        msg.attach(att)

        try:
            if mail_ssl in ['1', 1]:
                mail = smtplib.SMTP_SSL(timeout=60)
            else:
                mail = smtplib.SMTP(timeout=60)

            mail.connect(mail_host, int(mail_port))
            mail.ehlo()

            if mail_username and mail_password:
                mail.login(mail_username, mail_password)

            mail.sendmail(msg['from'], msg['to'], msg.as_string())
            mail.close()
            print "done."
        except Exception, e:
            print "fail:",e

    def make_html(self, user, feeds, save_file=False):

        if self.template_file:
            fp = open(self.template_file, 'r')
            t = template.Template(fp.read())
            fp.close()
        else:
            t  = template.Template(TEMPLATES['book.html'])

        content = t.generate(
            user = user,
            feeds = feeds
        )
    
        if save_file:
            data_dir = os.path.join(self.work_dir, 'data')
            if not os.path.exists(data_dir):
                os.makedirs( data_dir )
            
            fp = open(os.path.join(data_dir,
                'google-reader-%s.html' % time.strftime('%H-%M-%S') ), 'w')
            fp.write(content)
            fp.close()
    
        return content
        
    def make_mobi(self, user, feeds, format = 2):
        """docstring for make_mobi"""
        
        print "generate .mobi file... "
        
        data_dir = os.path.join(self.work_dir, 'data')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        for tpl in TEMPLATES:
            if tpl is 'book.html':
                continue
                
            t = template.Template(TEMPLATES[tpl])
            content = t.generate(
                user = user,
                feeds = feeds,
                uuid = uuid.uuid1(),
                format = format
            )
            
            fp = open(os.path.join(data_dir, tpl), 'wb')
            fp.write(content)
            fp.close()

        mobi_file = "GoogleReader(%s).mobi"% \
                time.strftime('%m-%dT%Hh%Mm')
        opf_file = os.path.join(data_dir, "content.opf")

        subprocess.call('%s  %s -o "%s" > log.txt' %
                (kindlegen, opf_file, mobi_file), shell=True)

        mobi_file = os.path.join(data_dir, mobi_file)
        if os.path.isfile(mobi_file) is False:
            print "failed!"
            return None
        else:
            fsize = os.path.getsize(mobi_file)
            print ".mobi save as: %s(%.2fMB)" %  (mobi_file, fsize/1048576)
            return mobi_file

    def parse_summary(self, summary, link):
        """处理文章"""

        soup = BeautifulSoup(summary)

        for span in list(soup.findAll(attrs={ "style" : "display: none;" })):
            span.extract()

        for attr in self.remove_attributes:
            for x in soup.findAll(attrs={attr:True}):
                del x[attr]

        for tag in soup.findAll(self.remove_tags):
            tag.extract()

        img_count = 0
        for img in list(soup.findAll('img')):
            if (self.max_image_number >= 0  and img_count >= self.max_image_number) \
                or img.has_key('src') is False \
                or img['src'].startswith("http://union.vancl.com/") \
                or img['src'].startswith("http://www1.feedsky.com/") \
                or img['src'].startswith("http://feed.feedsky.com/~flare/"):
                img.extract()
            else:
                try:
                    localimage = self.down_image(img['src'], link)

                    if localimage:
                        img['src'] = localimage
                        img_count = img_count + 1
                    else:
                        img.extract()
                except Exception, e:
                    print e
                    img.extract()

        return soup.renderContents('utf-8')

    def down_image(self, url, referer=None, filename=None):
        """download image"""

        print "download: %s" % url,

        url = escape.utf8(url)
        image_guid = hashlib.sha1(url).hexdigest()
        convert_image = self.get_config('reader', 'convert_image')

        x = url.split('.')
        ext = 'jpg'
        if len(x) > 1:
            ext = x[-1]

            if len(ext) > 4:
                ext = ext[0:3]

            ext = re.sub('[^a-zA-Z]','', ext)
            ext = ext.lower()

            if ext not in ['jpg', 'jpeg', 'gif','png','bmp']:
                ext = 'jpg'

        y = url.split('/')
        h = hashlib.sha1(str(y[2])).hexdigest()

        hash_dir = os.path.join(h[0:1], h[1:2])
        filename = image_guid + '.' + ext

        img_dir  = os.path.join(self.work_dir, 'data', 'images', hash_dir)
        fullname = os.path.join(img_dir, filename)

        localimage = 'images/%s/%s' % (hash_dir, filename)
        if os.path.isfile(fullname) is False:
            if not os.path.exists(img_dir):
                os.makedirs( img_dir )
            try:
                req = urllib2.Request(url)
                req.add_header('User-Agent', self.user_agent)
                req.add_header('Accept-Language', 'zh-cn,zh;q=0.7,nd;q=0.3')

                if referer is not None:
                    req.add_header('Referer', referer)

                response = urllib2.urlopen(req)

                localFile = open(fullname, 'wb')
                localFile.write(response.read())

                response.close()
                localFile.close()
                if convert_image :
                    os.system('convert -colorspace gray  \'%s[0]\' \
                            %s'% (fullname, fullname)
                            )
                print "done."
            except Exception, e:
                print 'fail: %s' % e
                localimage = False
            finally:
                localFile, response, req = None, None, None
        else:
            print "exists."

        return localimage

    def main(self):
        username = self.get_config('reader', 'username')
        password = self.get_config('reader', 'password')

        if not password and self.password:
            password = self.password

        if not username or not password:
            raise Exception("google reader's username or password is empty!")

        auth = ClientAuth(username, password)
        reader = GoogleReader(auth)
        user = reader.getUserInfo()
        reader.buildSubscriptionList()
        categoires = reader.getCategories()
        
        skip_categories = self.get_config('reader', 'skip_categories')
        select_categories = self.get_config('reader', 'select_categories')
        started_items = self.get_config('reader', 'started_items')
        
        feeds = {}
        skips = []
        selects = []

        if skip_categories:
            skip_categories = skip_categories.split(',')

            for c in skip_categories:
                if c: skips.append(c.encode('utf-8').strip())

            skip_categories = None

        if select_categories:
            select_categories = select_categories.split(',')
            
            for c in select_categories:
                if c: selects.append(c.encode('utf-8').strip())
            
            select_categories = None
            
        if started_items.isdigit() and int(started_items) is 1:
            sf = SpecialFeed(reader, "starred")
            sf.title = u"加星标的条目"
            feeds[sf.id] = sf

        capture_feeds = selects
        for category in categoires:
            if category.label.encode("utf-8") in capture_feeds:
                print 'select category: %s' % category.label.encode("utf-8")
                fd = category.getFeeds()
                for f in fd:
                    if f.id not in feeds:
                        feeds[f.id] = f
                fd = None
            else:
                if iswindows:
                    category.label = category.label.encode("gbk")
                print 'skip category: %s' % category.label.encode("utf-8")
        
        max_items_number = self.get_config('reader', 'max_items_number')
        try:
            mark_read = string.atoi(self.get_config('reader', 'mark_read'))
        except :
            mark_read = 0
        exclude_read = self.get_config('reader', 'exclude_read')
        max_image_per_article = self.get_config('reader', 'max_image_per_article')

        try: 
            max_image_per_article = int(max_image_per_article)
            self.max_image_number = max_image_per_article
        except:
            pass
        
        if max_items_number and max_items_number.isdigit():
            max_items_number = int(max_items_number)
        else:
            max_items_number = 50
                
        if exclude_read is None or not exclude_read.isdigit() or int(exclude_read) is 1:
            exclude_read = True
        else:
            exclude_read = False
            
        feed_idx,work_idx,updated_items = 0, 1, 0
        
        feed_num, current_feed = len(feeds), 0
        updated_feeds = []

        for feed_id in feeds:
            feed = feeds[feed_id]
            current_feed = current_feed + 1
            print "\nget [%s/%s]: %s" % (current_feed, feed_num, feed.id)
            
            try:
                feed_data = reader.getFeedContent(feed, exclude_read, number=max_items_number)
            
                item_idx = 1
                for item in feed_data['items']:
                    for category in item.get('categories', []):
                        if category.endswith('/state/com.google/reading-list'):
                            content = item.get('content', item.get('summary', {})).get('content', '')
                            url    = None
                            for alternate in item.get('alternate', []):
                                if alternate.get('type', '') == 'text/html':
                                    url = alternate['href']
                                    break
                                
                            if content:
                                item['content'] = self.parse_summary(content, url)
                                item['idx'] = item_idx
                                item = Item(reader, item, feed)
                                item_idx += 1
                            break

                feed.item_count = len(feed.items)
                updated_items += feed.item_count
                
                if mark_read == 1:
                    if feed.item_count >= max_items_number:
                        for item in feed.items:
                            item.markRead()
                        print "mark %d items as read"% feed.item_count
                    elif feed.item_count > 0:
                        reader.markFeedAsRead(feed)
                        print "mark all items as read"
            
                if feed.item_count > 0:
                    feed_idx += 1
                    feed.idx = feed_idx
                    updated_feeds.append(feed)
                    print "update %s items." % feed.item_count
                else:
                    print "no update."
            except Exception, e:
                print "fail:", e
        
        print "\nParse feed finished!\n"
        if updated_items > 0:
            mail_enable = self.get_config('mail', 'mail_enable')
            mobi_file = self.make_mobi(user, updated_feeds)
            if mobi_file and mail_enable == '1':
                fp = open(mobi_file, 'rb')
                self.sendmail(fp.read(), 'mobi')
                fp.close()
        else:
            print "no feed update."

if __name__ == '__main__':
    if not kindlegen:
        print "Can't find kindlegen"
        sys.exit(1)

    st = time.time()
    print "welcome, start ..."
    
    try:
        kr = KindleReader()
        kr.main()
    except Exception, e:
        print e

    print "used time %.2fs" % (time.time()-st)
    print "done."
    # Most unix users will run this script directly from a terminal or as a cron
    # job, just exit when the job is done.
    if iswindows:
        raw_input("Press any key to exit...")

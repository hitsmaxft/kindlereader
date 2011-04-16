#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
#import time
import datetime
#import logging
import random
import hashlib
import re
import zlib, base64

from cgi import parse_qsl
from urllib import unquote, quote_plus

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import mail
from google.appengine.api import taskqueue
from google.appengine.api import memcache
from google.appengine.api import urlfetch

from lib.libgreader import *
from lib.tornado import template
from lib.tornado import ui_module
from lib.BeautifulSoup import BeautifulSoup
import lib.oauth2 as oauth
from lib.cookies import Cookies

from config import *
from l10n import *

TIMEZONE = 8

def decode_base64_and_inflate( b64string ):
    decoded_data = base64.b64decode( b64string )
    return zlib.decompress( decoded_data , -zlib.MAX_WBITS)

def deflate_and_base64_encode( string_val ):
    zlibbed_str = zlib.compress( string_val )
    compressed_string = zlibbed_str[2:-4]
    return base64.b64encode( compressed_string )

def new_queue_name( base_name="testqueue" ):
    """docstring for get_queue_name"""
    
    if billing_enabled:
        max_id = 49
    else:
        max_id = 4

    return "%s%s" % (base_name, random.randint(0, max_id))

class GoogleReaderUser(db.Model):
    kindle_email = db.StringProperty()
    categories = db.StringListProperty()
    make_read = db.BooleanProperty()
    max_item  = db.IntegerProperty()
    oauth_token = db.StringProperty()
    oauth_token_secret = db.StringProperty()
    access_token = db.StringProperty()
    access_secret = db.StringProperty()
    
    send_time = db.IntegerProperty()
    timezone = db.StringProperty()
    last_delivered = db.DateTimeProperty()
    expires = db.DateTimeProperty()
    
    user_token = db.StringProperty()

class DeliverLog(db.Model):
    email = db.EmailProperty()
    to = db.EmailProperty()
    time = db.StringProperty()
    datetime = db.DateTimeProperty()
    feeds = db.IntegerProperty()
    items = db.IntegerProperty()
    pages = db.IntegerProperty()
    status = db.StringProperty()
    
class UrlQueue(db.Model):
    kindle_email = db.StringProperty()
    url = db.StringProperty()
    url_hash = db.StringProperty()
    title = db.TextProperty()
    content = db.TextProperty()
    status = db.IntegerProperty()
    added = db.DateTimeProperty()

class BaseHandler(webapp.RequestHandler):
    max_item = 200
    
    remove_tags = ['script','object','video','embed','iframe','noscript']
    remove_attrs = ['title','width','height','onclick','onload']
    
    @property
    def kindle(self):
        try:
            user_agent = self.request.headers['User-Agent']
            
            if user_agent.lower().find('kindle/2.0') > 0:
                return 2
            elif user_agent.lower().find('kindle/3.0') > 0:
                return 3
            elif user_agent.lower().find('kindle') > 0:
                return True
            else:
                return False
        except Exception, e:
            return False

    @property
    def accept_lang(self):
        """docstring for bwr_lang"""
        
        langs = GetSupportedLanguages()
        cookies = Cookies(self, max_age = 86400, path = '/')
        
        lang = self.request.get('lang')
        
        if lang.startswith("zh"):
            lang = 'zh-Hans'
        
        if lang and lang in langs:
            cookies['lang'] = lang
            return lang
        
        if 'lang' in cookies and cookies['lang'] in langs:
            return cookies['lang']
        
        try:
            accept_language = self.request.headers['Accept-Language']
        except:
            accept_language = "zh"
        
        if accept_language.startswith("en"):
            return "en"
        else:
            return "zh-Hans"
    
    def local_time(self, fmt):
        return (datetime.datetime.utcnow()+datetime.timedelta(hours=TIMEZONE)).strftime(fmt)
    
    def get_greader_auth(self, gr):
        """docstring for get_greader_auth"""
        
        try:

            if not consumer_key or not consumer_secret:
                logging.error("oauth consumer_key or consumer_secret not set.")
                return None
            
            auth = OAuth2Method(consumer_key, consumer_secret, gr.access_token, gr.access_secret)
        
            return auth
        except Exception, e:
            logging.error("auth failed: %s, %s" % (gr.email, e))
            return False
            
    def get_greader_user(self, email):
        """docstring for get_greader_user"""
        
        gr = GoogleReaderUser.get_by_key_name(email)
        
        if not gr:
            gr = GoogleReaderUser(key_name=email)
            gr.send_time = 8
            gr.kindle_email = ""
            gr.categories = []
            gr.make_read = True
            gr.max_item = 50
            gr.expires = datetime.datetime.utcnow() + datetime.timedelta(days=90)
            gr.user_token = hashlib.md5(email+consumer_key).hexdigest()
            gr.put()
        
        return gr
    
    def log(self, email, to, feeds=0, items=0, pages=0, status='ok', key=None):
        """docstring for log"""

        if key:
            deliver_log = DeliverLog.get(key)

            if deliver_log:
                deliver_log.status = status
                deliver_log.feeds = feeds
                deliver_log.items = items
                deliver_log.pages = pages
                deliver_log.put()

                return deliver_log.key()

        key = DeliverLog(email = email,
                   to = to,
                   time = self.local_time('%Y-%m-%d %H:%M:%S'),
                   datetime = datetime.datetime.utcnow(),
                   feeds = feeds,
                   items = items,
                   pages = pages,
                   status = status).put()

        return key
    
    def render_string(self, path, **kwargs):
        """docstring for render_string"""
        
        user = users.get_current_user()
        
        if user:
            nickname = user.nickname()
        else:
            nickname = None
        
        l10n = GetMessages(self, self.accept_lang)
        
        return template.Loader(os.path.join(os.path.dirname(__file__), 'views')) \
                        .load(path).generate(
                            logout_url = users.create_logout_url("/"),
                            nickname = nickname,
                            kindle = self.kindle,
                            is_admin = users.is_current_user_admin(),
                            TIMEZONE = TIMEZONE,
                            l10n = l10n,
                            **kwargs)
                            
    def render(self, tempate_name, **args):
        html_data = self.render_string(tempate_name,
                            module_menu = ModuleMenu(self),
                            **args)
        
        html_data = re.sub(r'(\n)+', '\n', html_data)
        self.response.out.write(html_data)
    
    def make_html(self, tempate_name, **args):
        return template.Loader(os.path.join(os.path.dirname(__file__), 'views')) \
                        .load(tempate_name).generate(
                            TIMEZONE=TIMEZONE,
                            **args)
    
    def fulltext_by_instapaper(self, url):
        """docstring for get_fulltext_from_"""
        
        if not url:
            return False
            
        url = "http://www.instapaper.com/m?u=%s" % quote_plus(url)
        result = urlfetch.fetch(url)
        if result.status_code == 200:
            
            soup = BeautifulSoup(result.content)
            
            title = soup.html.head.title.string
            title = re.sub(r'(\n)+', '', title)
            
            for tag in soup.findAll(self.remove_tags):
                tag.extract()

            for tag in list(soup.findAll(attrs={"class":"bar top"})):
                tag.extract()
                
            for tag in list(soup.findAll(attrs={"class":"bar bottom"})):
                tag.extract()
            
            for tag in list(soup.findAll(attrs={"id":"text_controls_toggle"})):
                tag.extract()
                
            for tag in list(soup.findAll(attrs={"id":"text_controls"})):
                tag.extract()
    
            for tag in list(soup.findAll(attrs={"id":"editing_controls"})):
                tag.extract()
                    
            for attr in self.remove_attrs:
                for tag in soup.findAll(attrs={attr:True}):
                    del tag[attr]

            for img in list(soup.findAll('img')):
                img.extract()
                
            content = soup.renderContents('utf-8')
            
            soup = None
            
            return title, content
        else:
            logging.error(result.status_code)
            return False

class MainHandler(BaseHandler):
    """docstring for MainHandler"""
    
    def get(self):
        """docstring for get"""
        self.render('home.html', login_url=users.create_login_url("/"))
        
class QnAHandler(BaseHandler):
    """docstring for MainHandler"""

    def get(self):
        """docstring for get"""
        self.render('qna.html', login_url=users.create_login_url("/"))
    
class SettingHandler(BaseHandler):
    
    def get(self, success=False):
        user = users.get_current_user()
        
        gr = self.get_greader_user(user.email())
        
        gr_account, categories = None, None
        if gr:
            try:
                gu_id = "gu%s" % user.email()
                gc_id = "gc%s" % user.email()
                
                gr_account = memcache.get(gu_id)
                categories = memcache.get(gc_id)
                
                if not gr_account or not categories:
                    auth = self.get_greader_auth(gr)

                    userId = None
                    if gr_account:
                        userId = gr_account.get('userId')
                        
                    reader = GoogleReader(auth, userId)
                    
                    if not gr_account:
                        gr_account = reader.getUserInfo()
                        
                        if gr_account:
                            memcache.add(gu_id, gr_account)
                    
                    if not categories:
                        reader.buildSubscriptionList()
                        categories = reader.getCategories()
                        starred_c = Category(reader, u"加星标的条目", GoogleReader.TAG_STARRED)
                        categories.append(starred_c)
                    
                    if not categories or len(categories) == 0:
                        cat = Category(reader, GoogleReader.UNCATEGORIZED_LABEL, GoogleReader.UNCATEGORIZED_ID)
                        categories = [cat]
                    else:
                        memcache.add(gc_id, categories, 3600)
                        
            except Exception, e:
                logging.warning("get greader failed, user:%s, exception: %s" % (user.email(), e))
            
            if not gr.expires:
                gr.expires = datetime.datetime.utcnow() + datetime.timedelta(days=90)
                gr.put()
               
            if not gr.user_token:
                gr.user_token = hashlib.md5(user.email()+consumer_key).hexdigest()
                gr.put()
        
        self.render('setting.html',
                user = user.nickname(),
                gr = gr,
                mail_sender = mail_sender,
                gr_account = gr_account,
                categories = categories,
                success = success
            )
                
    def post(self):
        """docstring for post"""
        
        user = users.get_current_user()
        
        kindle_email = self.request.get("kindle_email").strip()
        send_time = self.request.get("send_time")
        make_read = self.request.get("make_read")
        categories = self.request.get_all("categories")
        max_item = self.request.get("max_item")
        
        if make_read and make_read == '1':
            make_read = True
        else:
            make_read = False
            
        if not categories:
            categories = []
            
        if not max_item.isdigit():
            max_item = 50
        elif int(max_item) > self.max_item:
            max_item = self.max_item
        else:
            max_item = int(max_item)
            
        if not send_time.isdigit() \
            or int(send_time) not in range(0, 24):
            
            send_time = 8
        else:
            send_time = int(send_time)
    
        gr = GoogleReaderUser.get_by_key_name(user.email())
        gr.kindle_email = kindle_email
        gr.send_time = send_time
        gr.categories = categories
        gr.make_read = make_read
        gr.max_item = max_item

        gr.put()
        self.get(True)

class LogsHandler(BaseHandler):
    
    def get(self):
        
        user = users.get_current_user()
        logs = DeliverLog.gql("WHERE email = :email ORDER BY time DESC limit 10", email=user.email())
        
        self.render('logs.html', logs=logs)
        
class CancelAccountHandler(BaseHandler):
    
    def get(self):
        self.render('cancel_account.html', consumer_key=consumer_key)
    
    def post(self):        
        confirm = self.request.get("confirm")

        if not confirm:
            self.get()
            return
        
        user = users.get_current_user()
        
        gu = GoogleReaderUser.get_by_key_name(user.email())
        if gu:
            gu.delete()
            
        logs = DeliverLog.gql("WHERE email = :email ORDER BY time DESC", email=user.email())
        db.delete(logs)
        
        self.redirect(users.create_logout_url("/"))
          
class OAuthAuthHandler(BaseHandler):
    """docstring for OAuthHandler"""

    def get(self, mode=None):
        """docstring for get"""
        
        user = users.get_current_user()
        
        consumer = oauth.Consumer(consumer_key, consumer_secret)
        
        if mode == 'verify':
            
            oauth_token = self.request.get('oauth_token')
            gr = self.get_greader_user(user.email())
            
            if oauth_token != gr.oauth_token:
                self.redirect("/")
                return 
            
            token = oauth.Token(gr.oauth_token, gr.oauth_token_secret)
            client = oauth.Client(consumer, token)
            resp, content = client.request(OAuthMethod.ACCESS_TOKEN_URL, "POST")
            
            if resp['status'] == '200':
                access_token = dict(parse_qsl(content))
            
                gr.access_token = access_token['oauth_token']
                gr.access_secret = access_token['oauth_token_secret']
                gr.oauth_token = None
                gr.oauth_token_secret = None
                gr.put()
                
                memcache.delete("gu%s" % user.email())
                memcache.delete("gc%s" % user.email())
            
                self.render('oauth.html', success=True, fail=False)
            else:
                self.render('oauth.html', success=False, fail=True)
        else:
            client = oauth.Client(consumer)
            resp, content = client.request(OAuthMethod.REQUEST_TOKEN_URL, "GET")
            
            if resp['status'] == '200':
                
                request_token = dict(parse_qsl(content))
                gr = self.get_greader_user(user.email())
            
                gr.oauth_token = request_token['oauth_token']
                gr.oauth_token_secret = request_token['oauth_token_secret']
                gr.put()

                authorize_url = "%s?oauth_token=%s&oauth_callback=%s" % (OAuthMethod.AUTHORIZE_URL, request_token['oauth_token'],'%s/verify' % self.request.url)
                
                self.render('oauth.html', success=False, fail=False, authorize_url=authorize_url)
            else:
                self.render('oauth.html', success=False, fail=True)
        
class DeliverHandler(BaseHandler):
    """docstring for CronHandler"""
    
    def get(self):
        """docstring for get"""
        
        test = self.request.get('test')
        debug = self.request.get('debug')
        user = users.get_current_user()
        
        if user and test:
            gr_user = GoogleReaderUser.get_by_key_name(user.email())
            
            if not gr_user \
                or not gr_user.kindle_email \
                or not gr_user.categories \
                or not gr_user.access_token \
                or not gr_user.access_secret:
                
                self.response.out.write("fail")
            else:
                key = self.log(user.email(), gr_user.kindle_email, 0, 0, 0, status="queueing")
                queue_name = new_queue_name("testqueue") #"testqueue%s" % random.randint(0, 14)
                taskqueue.add(url='/worker',
                              queue_name=queue_name,
                              method='GET',
                              params={'email': gr_user.key().name(), 'log_key':key })
                              
                self.response.out.write('ok')
                
        elif self.request.headers.get('X-AppEngine-Cron') \
            or (users.is_current_user_admin() and debug):
            
            h = int(self.local_time("%H")) + 1
            
            if h > 24:
                h -= 24
                
            # gr_users = GoogleReaderUser.gql("WHERE send_time = :send_time and expires >= :expires", send_time=h, expires=datetime.datetime.utcnow())
            gr_users = GoogleReaderUser.gql("WHERE send_time = :send_time", send_time=h)
            send_time = datetime.datetime.strptime(self.local_time("%Y-%m-%d %H:00:00"), "%Y-%m-%d %H:%M:%S") - datetime.timedelta(hours=(TIMEZONE-1))

            task_num = 0
            for gr_user in gr_users:
                if gr_user.kindle_email \
                    or gr_user.access_token \
                    or gr_user.access_secret \
                    and gr_user.categories:
                    
                    queue_name = new_queue_name("dequeue") #"dequeue%s" % random.randint(0, 49)
                    taskqueue.add(url='/worker',
                                  queue_name = queue_name,
                                  method = 'GET',
                                  eta = send_time,
                                  params={'email': gr_user.key().name()})
                                  
                    task_num += 1
            
            logging.info("Cron run success at %s and added %s tasks for %s " % (self.local_time("%Y-%m-%d %H:%M:%S"), task_num, h))
            self.response.out.write("ok")

class BookmarkletHandler(BaseHandler):
    """docstring for MainHandler"""

    def get(self):
        """docstring for get"""
        user_token = self.request.get("k")
        self.render('bookmarklet.js', key=user_token)
            
class Post_V1Handler(BaseHandler):
    """docstring for Post_V1Handler"""
    
    def get(self):
        """docstring for get"""
        self.post()
    
    def post(self):
        """docstring for post"""
        
        url        = self.request.get("u")
        user_token = self.request.get("k")
        action     = self.request.get("a") # 1 和google reader一起投递, 2 马上投递
        
        title      = self.request.get("t")
        content    = self.request.get("b")
        
        if not user_token:
            u = users.get_current_user()
            
            if u:
                gr_user = GoogleReaderUser.get_by_key_name(u.email())
            else:
                gr_user = None
                
            if gr_user and gr_user.user_token: user_token = gr_user.user_token
            
        if not user_token or not url:
            return
            
        grs = GoogleReaderUser.gql("WHERE user_token =:user_token", user_token = user_token).fetch(limit=1)
        
        if grs:
            user = grs[0]
        else:
            user = None
            
        if user and user.kindle_email:
            self.push(url, title, content, user.kindle_email, action)
        else:
            self.redirect("/setting")
    
    def push(self, url, title, content, kindle_email, action = 2):
        """docstring for push"""
        
        content = decode_base64_and_inflate( content[4:] )
        
        if action.isdigit() and int(action) is 2: # push now
            mail.send_mail(sender = mail_sender,
                      to = kindle_email,
                      subject = "Convert",
                      body = "deliver from http://reader.dogear.mobi",
                      attachments=[("%s.html" % title, content)])
        else:
            q = UrlQueue()
            q.kindle_email = kindle_email
            q.url = url
            q.title = title
            q.content = unicode(content, 'utf-8')
            q.status = 0
            q.added = datetime.datetime.utcnow()
            q.put()
        
        # queue_name = new_queue_name("dequeue")
        # 
        # taskqueue.add(url='/push_worker',
        #               queue_name = queue_name,
        #               method = 'POST',
        #               params={'u': url, 't': kindle_email, 'a': action})
        
        self.response.out.write("""<html>
        <body style="color: #222; background-color: #fff; text-align: center; margin: 0px; font-family: Georgia, Times, serif; font-size: 26px;">
        <div style="text-align: center; width: 80%; padding-bottom: 1px; margin: 0 auto 15px auto; font-size: 14px; border-bottom: 1px solid #ccc; color: #333;">Dogear</div>
        Saved!
        </body>
        </html>""")

class PostWorkerHandler(BaseHandler):
    
    def post(self):
        
        url = self.request.get("u")
        kindle_email = self.request.get("t")
        action = self.request.get("a")
        
        if not url or not kindle_email:
            logging.warning("url or kindle email not set.")
            return
        
        (title, content) = self.fulltext_by_instapaper(url)

        if content is not False:
            
            if action.isdigit() and int(action) is 2: # push now
                mail.send_mail(sender = mail_sender,
                          to = kindle_email,
                          subject = "Convert",
                          body = "deliver from http://reader.dogear.mobi",
                          attachments=[("%s.html" % title, content)])
            else:
                q = UrlQueue()
                q.kindle_email = kindle_email
                q.url = url
                q.title = title
                q.content = unicode(content)
                q.status = 0
                q.added = datetime.datetime.utcnow()
                q.put()
        content = None

class MailHandler(BaseHandler):
    """docstring for TestHandler"""

    def get(self):
        return
        """docstring for get"""
        gr_users = GoogleReaderUser.all()
        
        for gr_user in gr_users:
            taskqueue.add(url='/mail',
                          method = 'POST',
                          params={'email':gr_user.key().name()})
                          
            self.response.out.write("sent to %s." % gr_user.key().name())
    
    def post(self):
        
        email = self.request.get('email')
        mail.send_mail(sender = "kindlereader<feeds@dogear.mobi>",
                      to = email,
                      subject = u"请重新设置投递分类",
                      body = u"""Hi,
    Kinldereader(http://feeder.dogear.mobi)系统升级出错，造成原设置分类信息丢失，请登录kindlereader重新设置，请凉解！
                        
jiedan.""")

class FeedbackHandler(BaseHandler):
    """docstring for CommentsHandler"""
    
    def get(self):
        """docstring for get"""
        self.render("feedback.html")

class CheckinHandler(BaseHandler):
    """docstring for checkinHandler"""
    
    def post(self):
        user = users.get_current_user()

        if user:
            gr = GoogleReaderUser.get_by_key_name(user.email())
        
            if gr:
                gr.expires = datetime.datetime.utcnow() + datetime.timedelta(days=90)
                gr.put()
        
                self.response.out.write(gr.expires.strftime("%Y-%m-%d"))
                return
        
        self.response.out.write("fail")
               
class WorkerHandler(BaseHandler):
    
    remove_tags = ['img','script', 'object','video','embed','iframe','noscript']
    remove_attrs = ['class','id','title','width','height','onclick','onload']
    
    updated_items = 0
    updated_feeds = 0
    updated_pages = 0
    
    def get(self):
        
        email = self.request.get('email')
        log_key = self.request.get('log_key')
        
        if not email:
            logging.warning("email must not be empty")
            return
        
        gr = GoogleReaderUser.get_by_key_name(email)
        
        if not gr or not gr.kindle_email:
            return
            
        gr_data = self.parser_gr(gr, email, log_key)
        
        html_data = self.parser_page(gr)
        
        self.sendmail(gr.kindle_email, gr_data, html_data)
        
        self.log(email, gr.kindle_email, self.updated_feeds, self.updated_items, self.updated_pages, key=log_key)
        logging.info('%s delivered to %s %s items of %s feeds and %s pages for %s' % (self.local_time('%Y-%m-%d %H:%M:%S'), gr.kindle_email, self.updated_items, self.updated_feeds, self.updated_pages, email))
        
        gr_data, html_data = None, None
        del gr_data, html_data
        
    def parser_page(self, gr):
        """docstring for fname"""

        urls = UrlQueue.gql("WHERE status = 0 and kindle_email =:email limit 100", email=gr.kindle_email)
        pages, idx = [], 0
        
        if urls:
            for page in urls:
                
                item = {
                    'idx':idx,
                    'url':page.url,
                    'title':page.title,
                    'content':page.content
                }
                
                pages.append(item)
                page.delete()
                
                idx += 1
        
        if idx > 1:
            self.updated_pages = idx
            return self.make_html('pages.html', pages = pages)
        else:
            logging.debug("no page for %s" % gr.kindle_email)
            return None
    
    def parser_gr(self, gr, email, log_key):
    
        if not gr \
            or not gr.kindle_email \
            or not gr.categories \
            or not gr.access_token \
            or not gr.access_secret:
            
            logging.warning("Setting error, email: %s" % email)
            return
        
        auth = self.get_greader_auth(gr)
        
        if not auth:
            self.log(email, gr.kindle_email, 0, 0, 0, 'Auth failed', key=log_key)
            return
        
        gr_user = memcache.get("gu%s" % email)

        userId = None
        if gr_user:
            userId = gr_user.get('userId')
            
        reader = GoogleReader(auth, userId)
        
        if not gr_user:
            
            try:
                gr_user = reader.getUserInfo()
            except:
                self.log(email, gr.kindle_email, 0, 0, 0, "Can't get user info.", key=log_key)
                return
        
        try:
            reader.buildSubscriptionList()
            categories = reader.getCategories()
        except:
            self.log(email, gr.kindle_email, 0, 0, 0, "Can't get subscription list.", key=log_key)
            return
            
        # parent = SpliceFeed(reader, u"推荐的条目")
        # overTime = "%.0f" % time.mktime((datetime.datetime.utcnow() - datetime.timedelta(days=1)).timetuple())
        # feed_data = reader.getSpliceContent(True, number=50, overTime=overTime)
        # 
        # 
        # self.response.out.write(feed_data)
        # 
        # return
            
        feeds = {}
        
        if GoogleReader.TAG_STARRED in gr.categories:
            sf = SpecialFeed(reader, "starred")
            sf.title = u"加星标的条目"
            feeds[sf.id] = sf
        
        for category in categories:
        
            if category.label in gr.categories:
                fd = category.getFeeds()
                for f in fd:
                    if f.id not in feeds:
                        feeds[f.id] = f

        if gr.max_item > self.max_item:
            gr.max_item = self.max_item
        elif gr.max_item is 0:
            return
        
        feed_idx, updated_items = 0, 0
        updated_feeds = []
                
        for feed_id in feeds:
            feed = feeds[feed_id]
            
            try:
                
                if hasattr(feed, 'type'):
                    isSpecialFeed = True
                else:
                    isSpecialFeed = False
                    
                max_item = gr.max_item
                
                if isSpecialFeed and feed.type == 'starred':
                    max_item = 100
                    excludeRead = False
                    overTime = "%.0f" % time.mktime((datetime.datetime.utcnow() - datetime.timedelta(days=1)).timetuple())
                else:
                    overTime = None
                    excludeRead = True
                
                feed_data = reader.getFeedContent(feed, excludeRead, number=max_item, overTime=overTime)
                
                item_idx = 1
                for item in feed_data['items']:
                    
                    if isSpecialFeed and feed.type == 'starred':
                        content = item.get('content', item.get('summary', {})).get('content', '')
                        if content:
                            item['content'] = self.parse_content(content)
                            item['idx'] = item_idx
                            item = Item(reader, item, feed)
                            item_idx += 1
                    else:
                        for category in item.get('categories', []):
                            if category.endswith('/state/com.google/reading-list'):
                                content = item.get('content', item.get('summary', {})).get('content', '')
                                if content:
                                    item['content'] = self.parse_content(content)
                                    item['idx'] = item_idx
                                    item = Item(reader, item, feed)
                                    item_idx += 1
                                break
                
                feed_data = None
                del feed_data
                
                feed.item_count = len(feed.items)
                updated_items += feed.item_count
                
                if gr.make_read:
                    if feed.item_count >= gr.max_item:
                        for item in feed.items:
                            item.markRead()
                    elif feed.item_count > 0:
                        reader.markFeedAsRead(feed)

                if feed.item_count > 0:
                    feed_idx += 1
                    feed.idx = feed_idx
                    updated_feeds.append(feed)
                    logging.debug("update %s items." % feed.item_count)
                else:
                    logging.debug("no update.")
                
                if feed_idx > 30 or updated_items > 1000:
                    break
                
            except Exception, e:
                logging.error("fail: %s" % e)
                
        gr_data = None

        if updated_items > 0:
            gr_data = self.make_html('feeds.html',
                            user = gr_user,
                            feeds = updated_feeds,
                        )
        
        self.updated_items = updated_items
        self.updated_feeds = feed_idx
        
        # gr.last_delivered = datetime.datetime.utcnow()
        # gr.put()
        
        updated_feeds = None
        del updated_feeds
        
        return gr_data
        
    def parse_content(self, content):
        
        soup = BeautifulSoup(content)
        
        for tag in soup.findAll(self.remove_tags):
            tag.extract()
                
        for attr in self.remove_attrs:
            for tag in soup.findAll(attrs={attr:True}):
                del tag[attr]

        content = soup.renderContents('utf-8')
        soup = None
        del soup
            
        return content
    
    def sendmail(self, to, gr_data=None, html_data=None):
        """docstring for mail"""
        
        
        if not gr_data and not html_data:
            return
        
        if not mail_sender:
            logging.error("mail sender not set.")
        else:
            
            attachments = []
            
            if gr_data:
                attachments.append(("Google reader(%s).html" % self.local_time("%m-%d %Hh%Mm"), gr_data))
            
            if html_data:
                attachments.append(("Read later(%s).html" % self.local_time("%m-%d %Hh%Mm"), html_data))
                
            mail.send_mail(sender = mail_sender,
                          to = to,
                          subject = "Convert",
                          body = "deliver from http://reader.dogear.mobi",
                          attachments=attachments)
        
        gr_data, html_data  = None, None
                          
class EditItemTagHandler(BaseHandler):
    """docstring for AddTagItemHandler"""
    
    def post(self):
        """docstring for post"""
        action = self.request.get('a')
        id = self.request.get('i')
        tag = self.request.get('t')
        token = self.request.get('token')
        email = self.request.get('e')
        
        if action not in ['a', 'r']:
            return
        
        if not email:
            logging.warning("email must not be empty")
            return
            
        if tag == 'read':
            tag = GoogleReader.TAG_READ
        elif tag == 'starred':
            tag = GoogleReader.TAG_STARRED
        elif tag == 'shared':
            tag = GoogleReader.TAG_SHARED
        else:
            return
        
        gr = GoogleReaderUser.get_by_key_name(email)
        
        if not gr \
            or not gr.kindle_email \
            or not gr.categories \
            or not gr.access_token \
            or not gr.access_secret:
            
            logging.warning("Setting error, email: %s" % email)
            return
        
        auth = self.get_greader_auth(gr)
        reader = GoogleReader(auth)
        
        if action == 'a':
            reader.httpPost(GoogleReader.EDIT_TAG_URL, {'i': id, 'a': tag, 'ac': 'edit-tags', 'T': token })
        elif action == 'r':
            reader.httpPost(GoogleReader.EDIT_TAG_URL, {'i': id, 'r': tag, 'ac': 'edit-tags', 'T': token })

#kindle's reader
class ReaderHandler(BaseHandler):
    """docstring for ReaderHandler"""
    
    def init(self):
        """docstring for init"""
        self.user = users.get_current_user()
        gr = GoogleReaderUser.get_by_key_name(self.user.email())
        
        if not gr \
            or not gr.access_token \
            or not gr.access_secret:

            return False
            
        auth = self.get_greader_auth(gr)

        if not auth:
            return False

        self.gr_user = memcache.get("gu%s" % self.user.email())
        
        userId = None
        if self.gr_user:
            userId = self.gr_user.get('userId')
            
        self.reader = GoogleReader(auth, userId)
        
        if not self.gr_user:
            self.gr_user = self.reader.getUserInfo()
        
        self.reader.buildSubscriptionList()
        memcache.add("gu%s" % self.user.email(), self.gr_user)
        
        return True
        
    def get_items(self, fid, continuation="", from_cache=True):
        """docstring for get_items"""
        
        id = unquote(fid).decode('utf-8')
        if from_cache:
            feed_data = self.cache_items('get', self.reader.userId, fid, continuation)
        else:
            feed_data = None
        
        if id.startswith('feed/'):
            parent = self.reader.getFeed(id)
            parent.isFeed = True
            
            if not feed_data:
                feed_data = self.reader.getFeedContent(parent, True, number=20, continuation=continuation)
                
        elif id.startswith('user/-/state/com.google/'):
            type = id.replace('user/-/state/com.google/','', 1)
            parent = SpecialFeed(self.reader, type)
            parent.isFeed = False

            if type == 'starred':
                excludeRead = False
            else:
                excludeRead = True

            feed_data = self.reader.getFeedContent(parent, excludeRead, number=20, continuation=continuation)
            
        # elif id.statrwith('splice'):
        #     
        #     parent = SpliceFeed(self.reader, u"推荐的条目")
        #     overTime = "%.0f" % time.mktime((datetime.datetime.utcnow() - datetime.timedelta(days=1)).timetuple())
        #     feed_data = reader.getSpliceContent(True, number=50, overTime=overTime)
        else:
            parent = self.reader.getCategory(id)
            parent.isFeed = False
            
            if not feed_data:
                feed_data = self.reader.getCategoryContent(parent, True, number=20, continuation=continuation)

        self.cache_items('set', self.reader.userId, fid, continuation, feed_data)
        
        return parent, feed_data
    
    def cache_items(self, action, userId, id, c=None, items=None):
        """docstring for cache"""
        
        cache_id = "u%sf%sc%s" % (userId, quote_plus(id), c)
        cache_id = hashlib.md5(cache_id).hexdigest()
        
        if action == 'set':
            memcache.add(cache_id, items, 3600)
            return True
        else:
            return memcache.get(cache_id)
            
    def parse_content(self, content):
        
        try:
            soup = BeautifulSoup(content)
        
            for tag in soup.findAll(self.remove_tags):
                tag.extract()

            for attr in self.remove_attrs:
                for tag in soup.findAll(attrs={attr:True}):
                    del tag[attr]

            for img in list(soup.findAll('img')):
                if img.has_key('src') is False \
                    or img['src'].startswith("http://union.vancl.com/") \
                    or img['src'].startswith("http://www1.feedsky.com/") \
                    or img['src'].startswith("http://feed.feedsky.com/~flare/") \
                    or img['src'].startswitch("http://static.googleadsserving"):
                    img.extract()

            content = soup.renderContents('utf-8')
            soup = None
            del soup
        
            return content
        except Exception, e:
            return content
            
    def edit_item_tag(self, id, action, tag):
        """docstring for markRead"""
        
        queue_name = new_queue_name("dequeue")
        taskqueue.add(url='/edit_item_tag',
                      queue_name = queue_name,
                      method = 'POST',
                      params={'e': self.user.email(),
                              'i': id,
                              'token': self.reader.token,
                              't': tag,
                              'a': action
                            })
        
        
class ReaderIndexHandler(ReaderHandler):
    """docstring for ReaderHandler"""
    
    def get(self):
        """docstring for get"""
        
        if not self.init():
            self.redirect("/oauth")
            return
        
        uncategorized = self.reader.getCategory(GoogleReader.UNCATEGORIZED_ID)
        
        if uncategorized:
            uncategorized_feeds = uncategorized.getFeeds()
        else:
            uncategorized_feeds = None
        
        categories = self.reader.getCategories()
        
        self.render("reader_index.html",
                user = self.gr_user, 
                feeds = uncategorized_feeds,
                categories = categories)

class ReaderLabelHandler(ReaderHandler):
    """docstring for ReaderIndexHandler"""

    def get(self, label):
        """docstring for get"""
        self.init()

        label = unquote(label).decode('utf-8')
        category = self.reader.getCategory(label)
        feeds = category.getFeeds()

        self.render("reader_label.html",
                user = self.gr_user, 
                category = category,
                feeds = feeds, 
                #category.getFeeds()
                )

class ReaderViewHandler(ReaderHandler):
    """docstring for ReaderIndexHandler"""
    
    def get(self, fid):
        """docstring for get"""
        
        continuation = self.request.get("c")
        mark_read = self.request.get("m")
        
        if not self.init():
            self.redirect("/oauth")
            return

        parent, feed_data = self.get_items(fid, continuation, False)
        
        item_idx = 1
        
        if feed_data:
            for item in feed_data['items']:
                item['idx'] = item_idx
                
                content = item.get('content', item.get('summary', {})).get('content', '')
                if content:
                    item['content'] = content #self.parse_content(content)
                    
                item = Item(self.reader, item, parent)
                item_idx += 1
        
        parent.item_count = len(parent.items)
        
        if feed_data:
            parent.continuation = feed_data.get('continuation', '')
        else:
            parent.continuation = ""
        
        self.render("reader_feed.html",
                user = self.gr_user,
                parent = parent,
                continuation = continuation
            )

class ReaderItemHandler(ReaderHandler):
    """docstring for ReaderItemHandler"""
    
    def get(self, fid):
        """docstring for get"""
        
        continuation = self.request.get("c")
        index        = self.request.get("i")
        mark_read    = self.request.get("m")
        mark_star    = self.request.get("s")
        
        if index and index.isdigit():
            index = int(index)
        else:
            index = 1
        
        if not self.init():
            self.redirect("/oauth")
            return
        
        parent, feed_data = self.get_items(fid, continuation)
        
        item = None
        item_idx = 1
        for item in feed_data['items']:
            
            if item_idx == index:
                item['idx'] = item_idx
                
                content = item.get('content', item.get('summary', {})).get('content', '')
                if content:
                    item['content'] = self.parse_content(content)
                
                item = Item(self.reader, item, parent)
                
                if mark_read == 'u' and item.read:
                    item.markUnread()
                    # self.edit_item_tag(item.id, 'r', 'read')
                    item.read = False
                elif not item.read:
                    item.markRead()
                    # self.edit_item_tag(item.id, 'a', 'read')
                    item.read = True
                
                if mark_star == 'm' and not item.starred:
                    # self.edit_item_tag(item.id, 'a', 'starred')
                    item.star()
                elif mark_star == 'u' and item.starred:
                    # self.edit_item_tag(item.id, 'r', 'starred')
                    item.unStar()
                
                break
                
            item_idx += 1
            
        parent.continuation = feed_data.get('continuation', '')
        
        self.render("reader_item.html",
                user = self.gr_user, 
                parent = parent,
                item = item,
                continuation = continuation)


class RemoveLogHander(webapp.RequestHandler):
    """docstring for RemoveLogHander"""
    
    def get(self):
        """docstring for get"""
        query = DeliverLog.all()
        query.filter('datetime < ', datetime.datetime.utcnow() - datetime.timedelta(days=25))
        logs = query.fetch(10000)
        c = len(logs)
        db.delete(logs)
        self.response.out.write("%s lines log removed" % c)

# UI Modules
class ModuleMenu(ui_module.UIModule):
    
    def render(self, current=None):
            return self.render_string(
                "module-menu.html", current=current)

def main():
    logging.getLogger().setLevel(logging.INFO)
    application = webapp.WSGIApplication([
                        ('/', MainHandler),
                        ('/setting', SettingHandler),
                        ('/checkin', CheckinHandler),
                        ('/logs', LogsHandler),
                        ('/qna', QnAHandler),
                        ('/cancel_account', CancelAccountHandler),
                        ('/oauth/?(.*)', OAuthAuthHandler),
                        ('/mail', MailHandler),
                        ('/deliver', DeliverHandler),
                        ('/feedback', FeedbackHandler),
                        ('/worker', WorkerHandler),
                        ('/post_worker', PostWorkerHandler),
                        ('/j', BookmarkletHandler),
                        ('/post_v1', Post_V1Handler),
                        ('/reader/?', ReaderIndexHandler),
                        ('/reader/label/(.*)', ReaderLabelHandler),
                        ('/reader/view/(.*)', ReaderViewHandler),
                        ('/reader/item/(.*)', ReaderItemHandler),
                        ('/remove_logs', RemoveLogHander),
                    ], debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
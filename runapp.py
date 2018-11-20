#coding:utf-8
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

import torndb

import os.path
import urllib2
import urllib
import json
import re
import sys
sys.path.append("..")
import saltapi

from tornado.options import define, options
define("port", default=8070, help="run on the given port", type=int)

def message(mess, url):
    '消息模块'

    arg_message = {
        'mess': mess,
        'url': url
    }

    message = '''
    <script>
    alert ("%(mess)s")
    window.location.href="%(url)s"
    </script>
    ''' % arg_message

    return message

def list_all_dict(dict_a):
    if isinstance(dict_a, dict):  # 使用isinstance检测数据类型
        for x in range(len(dict_a)):
            temp_key = dict_a.keys()[x]
            temp_value = dict_a[temp_key]
            print"%s : %s" % (temp_key, temp_value)
            list_all_dict(temp_value)  # 自我调用实现无限遍
 
# BaseHandler 基类覆写 get_current_user
# 覆写后 RequestHandler 的current_user成员会有值(稍后解释实现源码) 
# 这里简单地判断请求带的 secure cookie 是否带有 user属性的值
class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")
 
# 实际业务类实现
class MainHandler(BaseHandler):
    def get(self): 
        # 判断 current_user, 如果不存在值,要求重定向到 login页面
        if not self.current_user: 
            self.redirect("/login")
            return
        name = tornado.escape.xhtml_escape(self.current_user)
        self.write("Hello, " + name)

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        return self.render("index.html")

class LoginHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('login.html')
    def post(self):
        self.set_secure_cookie("username", self.get_argument("username"))
        self.redirect("/")

class RemoteSoftHandler(tornado.web.RequestHandler):

    def get(self):

        clientiplist = []
        clientdb=torndb.Connection('localhost','clientdb','root','tornado123')
        minions = clientdb.query('select clientip from clienttable')
        for minion in minions:
            dbminion =  minion.values()[0].encode("GBK")
            clientiplist.append(dbminion)
        #print clientiplist
            

        #minion = ['192.168.188.17', '192.168.188.18',  '*']
        client = ['local_async', 'local', 'globe', 'wheel']
        return self.render("softinstall.html", soft="", client=client,minion=clientiplist)

    def post(self):
        
        clientiplist = []
        clientdb=torndb.Connection('localhost','clientdb','root','tornado123')
        minions = clientdb.query('select clientip from clienttable')
        for minion in minions:
            dbminion =  minion.values()[0].encode("GBK")
            clientiplist.append(dbminion)
        #print clientiplist
        
        mion = self.get_argument(u'minion')
        #print mion
        
        moremion = self.get_argument(u'textarea1').replace('\r\n',',')
        #print  self.get_argument(u'textarea1')
        print  moremion

        #minion = ['192.168.188.17', '192.168.188.18',  '*']
        cli = self.get_argument(u'client')
        client = ['local_async', 'local', 'globe', 'wheel']

        modules = self.get_arguments(u'module')
        print modules
        #print modules[0]
        softlist = []
        for mod in modules:
            #print mod
            paramsmod = {'client': cli, 'fun': 'state.sls', 'expr_form': 'list', 'tgt': moremion, 'arg1': mod}
            print paramsmod
            sapimod = saltapi.saltAPI()
            softinfomod = sapimod.saltCmd(paramsmod)
            softlist.append(softinfomod)
        return self.render("softinstall.html", soft=softlist,client=client,minion=clientiplist)

        #params = {'client': cli, 'fun': 'state.sls', 'tgt': minion, 'arg1': modules[0]}
        #print params

        #sapi = saltapi.saltAPI()
        #softinfo = sapi.saltCmd(params)

        #for m in range(len(softinfo)):
        #    for r in softinfo[m].values():
        #        list_all_dict(r)


class RemoteFileHandler(tornado.web.RequestHandler):
    def get(self):
        #self.write("配置管理功能还在开发中")
        sfile = os.listdir('/srv/salt/sourcefile/')
        self.render("filecp.html",sfile=sfile)

    def post(self):
        minion = self.get_argument(u'ip')
        sfile = self.get_argument(u'sfile')
        dfile = self.get_argument(u'dfile')
        params = {'client': 'local', 'fun': 'cp.get_file', 'tgt': minion,'arg1':'salt://sourcefile/%s' % sfile, 'arg2':'%s/%s' % (dfile,sfile)}
        print params

        sapi = saltapi.saltAPI()
        filecp = sapi.saltCmd(params)
        print filecp
        print filecp[-1].values()[0]
        if filecp[-1].values()[0] != False:
           self.write(message('配置下发成功！','/filecp'))
        self.write(message('配置下发失败！','/filecp'))


class JidStatusHandler(tornado.web.RequestHandler):
    def get(self):
        #self.write("状态管理功能还在开发中")
        clientiplist = []
        clientdb=torndb.Connection('localhost','clientdb','root','tornado123')
        minions = clientdb.query('select clientip from clienttable')
        for minion in minions:
            dbminion =  minion.values()[0].encode("GBK")
            clientiplist.append(dbminion)

        jidlist= []
        jidstatus = clientdb.query('select jid from jidstatus')

        for jidstatu in jidstatus:
            dbjidstatu = jidstatu.values()[0].encode("GBK")
            jidlist.append(dbjidstatu)


        return self.render("jidstatus.html",jidstatuoutput="",jidstatu=jidlist,minion=clientiplist)


    def post(self):
        clientiplist = []
        clientdb=torndb.Connection('localhost','clientdb','root','tornado123')
        minions = clientdb.query('select clientip from clienttable')
        for minion in minions:
            dbminion =  minion.values()[0].encode("GBK")
            clientiplist.append(dbminion)
        print clientiplist
        mion = self.get_argument(u'minion')
        print "post mion" ,mion
        newmion = '"'+mion+'"'
        print "post newmion" ,newmion

        jidlist= []
        jidstatus = clientdb.query('select jid from jidstatus where clientip= %s'%(newmion))
        for jidstatu in jidstatus:
            dbjidstatu = jidstatu.values()[0].encode("GBK")        
            jidlist.append(dbjidstatu)
        print jidlist
        

        ljid = self.get_argument(u'jidstatu')

        params = {'client': 'runner', 'fun': 'jobs.lookup_jid',  'jid': ljid}
        print params

        sapi = saltapi.saltAPI()
        jidstatuoutput = sapi.saltCmd(params)
        print jidstatuoutput

        return self.render("jidstatus.html",jidstatu=jidlist,jidstatuoutput=jidstatuoutput,minion=clientiplist)


class RemoteMinionHandler(tornado.web.RequestHandler):
    def get(self):
        functions = ['cmd.run', 'state.sls',  'test.echo']
        client = ['local','local_async ','globe', 'wheel']
        return self.render("minion.html", remotecmd="",functions=functions, client=client)

    def post(self):
        minion = self.get_argument(u'minion')
        arg1 = self.get_argument(u'arg1')
        fun = self.get_argument(u'functions')
        cli = self.get_argument(u'client')


        functions = [ 'cmd.run','state.sls',  'test.echo']
        client = ['local', 'local_async','globe', 'wheel']

        params = {'client': cli, 'fun': fun, 'tgt': minion, 'arg1': arg1}
        print params

        sapi = saltapi.saltAPI()
        remotecmd = sapi.saltCmd(params)
        print remotecmd

        return self.render("minion.html", remotecmd=remotecmd,functions=functions,client=client)


if __name__ == "__main__":

    tornado.options.parse_command_line()

    settings = {
    'debug' : True,
    'static_path' : os.path.join(os.path.dirname(__file__), "static") ,
    'template_path' : os.path.join(os.path.dirname(__file__), "templates") ,
    'cookie_secret': '+5M8+qKhTVmBI6gOetMIFciw6lBCiU9usa+lXgw/HCQ=',
    'login_url':'/login',
        }

    app = tornado.web.Application([
        (r"/", IndexHandler),                  #首页
	    (r"/login", LoginHandler),             #登陆页面 
        (r"/softinstall", RemoteSoftHandler),  #软件部署
        (r"/minions", RemoteMinionHandler),    #客户端管理
        (r"/filecp", RemoteFileHandler),       #配置下发
        (r"/jidstatus", JidStatusHandler)      #状态管理
    ],**settings)

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

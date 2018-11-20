#!/usr/bin/env python
#coding=utf-8
import ssl
import urllib2, urllib, json, re
 
class saltAPI:
    def __init__(self):
        ssl._create_default_https_context = ssl._create_unverified_context
        self.__url = 'https://124.250.36.224:8888'       #salt-api监控的地址和端口如:'https://124.250.36.224:8888'
        self.__user =  'saltapi'             #salt-api用户名
        self.__password = 'salt_123qazXSW'          #salt-api用户密码
        self.__token_id = self.salt_login()
 
    def salt_login(self):
        params = {'eauth': 'pam', 'username': self.__user, 'password': self.__password}
        encode = urllib.urlencode(params)
        obj = urllib.unquote(encode)
        headers = {'X-Auth-Token':''}
        url = self.__url + '/login'
        req = urllib2.Request(url, obj, headers)
        opener = urllib2.urlopen(req)
        content = json.loads(opener.read())
        try:
            token = content['return'][0]['token']
            return token
        except KeyError:
            raise KeyError
 
    def postRequest(self, obj, prefix='/'):
        url = self.__url + prefix
        headers = {'X-Auth-Token'   : self.__token_id}
        req = urllib2.Request(url, obj, headers)
        opener = urllib2.urlopen(req)
        content = json.loads(opener.read())
        return content['return']
 
    def saltCmd(self, params):
        obj = urllib.urlencode(params)
        obj, number = re.subn("arg\d", 'arg', obj)
        res = self.postRequest(obj)
        return res


def main():
    #以下是用来测试saltAPI类的部分
    sapi = saltAPI()
    params = {'client':'local', 'fun':'user.add', 'tgt':'172.21.1.*','arg1':'jack','arg2':'home=/home/jack/', 'arg3':'shell=/bin/bash'
}
    #params = {'client': 'runner', 'fun': 'jobs.lookup_jid', 'jid': '20150827163231404925'}
    #params = {'client':'local', 'fun':'test.ping', 'tgt':'某台服务器的key'}
    #params = {'client':'local', 'fun':'test.echo', 'tgt':'某台服务器的key', 'arg1':'hello'}
    #params = {'client':'local', 'fun':'test.ping', 'tgt':'某组服务器的组名', 'expr_form':'nodegroup'}
    
    test = sapi.saltCmd(params)
    print test
 
if __name__ == '__main__':
    main()

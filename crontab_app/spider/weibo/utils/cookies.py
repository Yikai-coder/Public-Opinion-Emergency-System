#-*- encoding:utf-8 -*-
import base64
import requests
import re
import rsa
import binascii

# def Get_cookies():
#     '''登陆新浪微博，获取登陆后的Cookie，返回到变量cookies中'''
#     username = input(u'请输入用户名：')
#     password = input(u'请输入密码：')

#     prelogin_url = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=aHVpeWFkYW5saSU0MDEyNi5jb20%3D&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.18)&_=1457524967315'
#     html = requests.get(prelogin_url).content.decode('utf-8')
#     print(html)

#     servertime = re.findall('"servertime":(.*?),',html,re.S)[0]
#     nonce = re.findall('"nonce":"(.*?)"',html,re.S)[0]
#     pubkey = re.findall('"pubkey":"(.*?)"',html,re.S)[0]
#     rsakv = re.findall('"rsakv":"(.*?)"',html,re.S)[0]

#     username = base64.b64encode(username) #加密用户名
#     rsaPublickey = int(pubkey, 16)
#     key = rsa.PublicKey(rsaPublickey, 65537) #创建公钥
#     message = str(servertime) + '\t' + str(nonce) + '\n' + str(password) #拼接明文js加密文件中得到
#     passwd = rsa.encrypt(message, key) #加密
#     passwd = binascii.b2a_hex(passwd) #将加密信息转换为16进制。

#     login_url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.4)'
#     data = {'entry': 'weibo',
#         'gateway': '1',
#         'from': '',
#         'savestate': '7',
#         'userticket': '1',
#         'ssosimplelogin': '1',
#         'vsnf': '1',
#         'vsnval': '',
#         'su': username,
#         'service': 'miniblog',
#         'servertime': servertime,
#         'nonce': nonce,
#         'pwencode': 'rsa2',
#         'sp': passwd,
#         'encoding': 'UTF-8',
#         'prelt': '115',
#         'rsakv' : rsakv,
#         'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
#         'returntype': 'META'
#         }
#     html = requests.post(login_url,data=data).content
#     urlnew = re.findall('location.replace\(\'(.*?)\'',html,re.S)[0]

#     #发送get请求并保存cookies
#     cookies = requests.get(urlnew).cookies
#     return cookies

import re
import rsa
import json
import time
import base64
import binascii
import requests


class WeiboLogin:

    def __init__(self, username, password):
        self.session = requests.Session()
        self.headers = {   # 伪装请求
            'Referer': 'https://weibo.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'
        }
        self.username = username
        self.password = password

    def get_username(self):
        """
        通过base64编码获取su的值
        """
        username_base64 = base64.b64encode(self.username.encode())
        return username_base64.decode()

    def get_json_data(self, su):
        """
        通过su参数发起第一次请求，获取pubkey和nonce的值
        """
        url = 'https://login.sina.com.cn/sso/prelogin.php'
        timestamp = int(time.time() * 1000)
        params = {
            'entry': 'weibo',
            'callback': 'sinaSSOController.preloginCallBack',
            'su': su,
            'rsakt': 'mod',
            'checkpin': '1',
            'client': 'ssologin.js(v1.4.19)',
            '_': timestamp
        }
        data = self.session.get(url=url, headers=self.headers, params=params).text
        json_data = json.loads(re.findall(r'\((.*?)\)', data, re.S)[0])
        return json_data

    def get_password(self, servertime, nonce, pubkey):
        """
        对密码进行rsa加密
        """
        stri = (str(servertime)+'\t'+str(nonce)+'\n'+self.password).encode()
        public_key = rsa.PublicKey(int(pubkey, 16), int('10001', 16))
        password = rsa.encrypt(stri, public_key)
        password = binascii.b2a_hex(password)
        return password.decode()

    def login_first(self):
        """
        发起第一次登录请求，获取登录请求跳转页redirect_login_url
        """
        su = self.get_username()
        json_data = self.get_json_data(su)
        sp = self.get_password(json_data['servertime'], json_data['nonce'], json_data['pubkey'])
        data = {
            'entry': 'weibo',
            'gateway': '1',
            'from': '',
            'savestate': '7',
            'qrcode_flag': 'false',
            'useticket': '1',
            'pagerefer': '',
            'vsnf': '1',
            'su': su,
            'service': 'miniblog',
            'servertime': json_data['servertime'],
            'nonce': json_data['nonce'],
            'pwencode': 'rsa2',
            'rsakv': json_data['rsakv'],
            'sp': sp,
            'sr': '2560*1440',
            'encoding': 'UTF-8',
            'prelt': '65',
            'url': 'https://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype': 'META'
        }
        # 首次登录请求地址
        login_url = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)'
        response = self.session.post(url=login_url, data=data, headers=self.headers)
        response.encoding = response.apparent_encoding
        try:
            redirect_login_url = re.findall(r'replace\("(.*?)"\)', response.text, re.S)[0]
            return redirect_login_url
        except:
            return '获取首次登录请求跳转页失败'

    def login_second(self):
        """
        发起第二次登录请求，再次获取登录请求跳转页arrURL
        """
        # 第二次登录请求地址
        url = self.login_first()
        response = self.session.get(url, headers=self.headers)
        response.encoding = response.apparent_encoding
        try:
            arr_url = json.loads(re.findall(r'setCrossDomainUrlList\((.*?)\)', response.text, re.S)[0])['arrURL'][0]
            return arr_url
        except:
            return '获取第二次登录请求跳转页失败'

    def login_finally(self):
        """
        发起最终登录请求，实现登录并跳转到用户微博首页
        """
        # 最终登录请求地址
        url = self.login_second()
        try:
            res = self.session.get(url, headers=self.headers)
            res.encoding = res.apparent_encoding
        except:
            return '登录失败，或为用户名或密码错误'
        try:
            # 获取用户id
            uid = json.loads(res.text[1:-4])['userinfo']['uniqueid']
            # 拼接用户微博首页
            user_home_url = 'https://www.weibo.com/u/{}/home'.format(uid)
            # 访问用户微博首页
            response = self.session.get(url=user_home_url, headers=self.headers)
            response.encoding = response.apparent_encoding
            title = re.findall(r'<title>(.*?)</title>', response.text, re.S)[0]
            if '我的首页' in title:
                return '登录成功'
            else:
                return '登录失败'
        except:
            return '获取最终登录请求跳转页失败'


if __name__ == '__main__':
    # 此处输入用户名和密码
    username = '13532785056'
    password = 'li010920'
    weibo = WeiboLogin(str(username), str(password))
    # 发起模拟登录
    print(weibo.login_finally())

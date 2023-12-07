# -*- coding:utf-8 -*-

from requests import Session # Session自动保持cookie，加快连接速度，减少代码量
from random import random # [0, 1)的随机数
from time import time, sleep # 获取时间戳需要用到time，等待用户需要用到sleep
from re import search # 正则匹配
from json import loads, dumps # json字符串转python dict


####----------修改这里--------------####
interval = 1 ## 检查登录状态的间隔(s)
model = '北京大学机房' ### 自定义机型
sIMei = '8d54de1fad47e55b' ### 填入sIMei  获取在https://1105583577.urlshare.cn
####--------------------------------####


x = Session() # 实例化Session
r = x.get(f'https://ssl.ptlogin2.qq.com/ptqrshow?appid=549000912&e=2&l=M&s=3&d=72&v=4&t={random()}&daid=5&pt_3rd_aid=0') # 获取二维码
with open('QRCode.png', 'wb') as f: f.write(r.content) # 写入二维码
print('请扫描二维码！(QRCode.png)')
sig = r.cookies['qrsig'] # 获取qrsig
# 计算ptqrtoken, 参考https://www.jianshu.com/p/17ec959b7324
e = 0
for i in sig:
    e += e << 5
    e += ord(i)
token = str(2147483647 & e)
while True: # 循环检查是否登录
    r = x.get(f'https://ssl.ptlogin2.qq.com/ptqrlogin?u1=https%3A%2F%2Fqzs.qzone.qq.com%2Fqzone%2Fv5%2Floginsucc.html%3Fpara%3Dizone&ptqrtoken={token}&ptredirect=0&h=1&t=1&g=1&from_ui=1&ptlang=2052&action=0-1-{int(time() * 1000)}&js_ver=10291&js_type=1&login_sig=&pt_uistyle=40&aid=549000912&daid=5&') # 接口
    data = eval(r.text[6:]) # 返回数据过滤并转为tuple，以便分析
    '''
    返回数据r.text示例
        未扫码
            二维码已失效: ptuiCB('65','0','','0','二维码已失效。(853563202)', '')
            二维码未失效: ptuiCB('66','0','','0','二维码未失效。(4087375736)', '')
        已扫码
            等待认证: ptuiCB('67','0','','0','二维码认证中。(3831518952)', '')
            登录成功: ptuiCB('0','0','https://ptlogin2.qzone.qq.com/check_sig?pttype=1&uin={QQ号}&service=ptqrlogin&nodirect=0&ptsigx=65cedf5e96324d51637235fa67c4dc7da1254fe840595af1c02cad9f55e8ab37c5cdac262dffafdeeddd812b0e309cc7131f9102b6763185f44096dbadb650a4&s_url=https%3A%2F%2Fqzs.qzone.qq.com%2Fqzone%2Fv5%2Floginsucc.html%3Fpara%3Dizone&f_url=&ptlang=2073&ptredirect=100&aid=549000912&daid=5&j_later=0&low_login_hour=0&regmaster=0&pt_login_type=3&pt_aid=0&pt_aaid=16&pt_light=0&pt_3rd_aid=0','0','登录成功！', '{QQ昵称}')
    '''
    code = data[0] # 返回的登录状态代码(str类型)
    if code == '66':
        print('二维码未失效，请扫码登录。')
    elif code == '0':
        print('登录成功！')
        flag = True
        break
    elif code == '67':
        print('请在手机上确认。')
    elif code == '65':
        print('二维码已失效，请重启脚本！')
        flag = False
        break
    sleep(interval) # 等待interval秒
if flag: # 登录成功
    qq = search(r'&uin=(\d+)&service=ptqrlogin', data[2]).groups()[0] # 筛选获取qq号
    # 计算g_tk，参考https://blog.csdn.net/qd_sharon/article/details/23393951
    skey = x.cookies['skey']
    hash = 5381
    for i in skey:
            hash += (hash << 5) + ord(i)
    g_tk = hash & 0x7fffffff
    print(f"您已登录为：{data[5]}({qq})") # 登录提示
    x.get(data[2]) # 跳转返回的验证页面
    load = { # 需要上传的数据
        'ts': int(time()*1000),
        'g_tk': g_tk,
        'data': dumps({"13031":{"req":{"sModel": model,"iAppType":3,"sIMei": sIMei,"sVer":"8.8.3.5470","sManu":"","lUin":int(qq),"bShowInfo":True,"sDesc":"","sModelShow": model}}}, separators=(',', ':')),
        'pt4_token': x.cookies['pt4_token']
    }
    r = x.get('https://proxy.vac.qq.com/cgi-bin/srfentry.fcgi', params=load).json() # 请求接口
    if r['ecode'] == 0: print('修改成功！')
    else:
        print('修改失败！以下为返回数据：')
        print(r)
input('运行结束！')

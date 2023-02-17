#!/usr/bin/env python3
#coding:utf-8
import datetime
from email.mime.text import MIMEText
import json
import re
import smtplib
import time
from random import random
import requests
import os
import pytz as pytz

from yzm.slider_yzm import build_post
from SpiderAgency import ua_change

def getTime(mode):
    utc_now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
    SHA_TZ = datetime.timezone(
        datetime.timedelta(hours=8),
        name='Asia/Shanghai',
    )
    # 北京时间
    beijing_now = utc_now.astimezone(SHA_TZ)
    fmt = '%Y-%m-%d %H:%M:%S'
    now_fmt =beijing_now.strftime(fmt)
    if mode == 0:
        return now_fmt[:10]
    else:
        return now_fmt[11:]  

tz = pytz.timezone('Asia/Shanghai') 
def userInfoRead():
    current_path = os.getcwd()
    with open(current_path + '/BadmintonXJTU/docs/user_config.json','r') as f:
      data = json.loads(f.read(),)
      return data

def email(text:str,info:dict):
    '''使用stmp邮箱服务发送邮件
    text:要发送的字符信息
    info[0]:email from whom, eg. ****@****.com
    info[1]:email to whom, eg. ****@****.com
    info[2]:smtp Sever地址,eg:smtp.qq.com
    info[3]:开放的端口号
    info[4]:授权密码而非账户密码
    '''
    msg = MIMEText(text, 'plain', 'utf-8')
    msg_From = info["from"];
    msg_To = info["to"]
    smtpSever = info["smtpServer"]
    smtpPort = info["port"]
    sqm = info["AuthorizationCode"]

    msg['from'] = msg_From
    msg['to'] = msg_To
    msg['subject'] = 'Python自动邮件-羽毛球场预约%s' % time.ctime()
    smtp = smtplib
    smtp = smtplib.SMTP_SSL(smtpSever)

    #smtplib的connect（连接到邮件服务器）、login（登陆验证）、sendmail（发送邮件）
    smtp.connect(smtpSever, smtpPort)
    smtp.login(msg_From, sqm)
    smtp.sendmail(msg_From, msg_To, str(msg))
    print("email已发送")
    smtp.quit()

class YiDongJiaoDa(object):
    def __init__(self,username,passward,PlatFlag:str,date='') -> None:
        '''
        username:登录平台用户名；passward：登录平台密码
        PlatFlag: '41' 一楼 '42'三楼
        date：要预定的日期，格式为2022-06-11
        '''
        self.username = username;
        self.passward = passward;
        self.session = requests.session();
        # self.session.keep_alive = False;
        self.session.headers['User-Agent'] = ua_change();
        print('随机配置UA信息',self.session.headers['User-Agent'])
        #41 一楼 42 三楼
        self.platid = PlatFlag
        self.allplat = {};
        self.userToken = ''
        
        # if date == '':
        #     today = datetime.datetime.today()
        #     five_days_after = today + datetime.timedelta(days=4)
        #     self.date = five_days_after.strftime("%Y-%m-%d")
        # else:
        self.date = date

    def login(self):
        try:
            url = "http://org.xjtu.edu.cn/openplatform//toon/auth/loginByPwd"
            data = {
                "acount":self.username,
                "pwd":self.passward
            }
            headers={
                "secretKey":"18a9d512c03745a791d92630bc0888f6"
            }
            r = self.session.post(url,json=data,headers=headers)
            data = json.loads(r.text)["data"]
            userToken = data['userToken']
            userId = data['memberId']
            orgId = data['orgId']
            self.userId = userId
            self.orgId = orgId
            self.userToken = userToken
            url = "http://org.xjtu.edu.cn/openplatform/toon/auth/generateTicket"
            params = {
                'personToken':userToken,
                'empNo':self.username
            }
            r = self.session.get(url,params=params,headers=headers)
            ticket = json.loads(r.text)['data']['ticket']

            return ticket
        except Exception as e:
            return e

    def login_again(self):
        url = 'http://org.xjtu.edu.cn/openplatform/toon/private/userLoginByToken'
        data={"userToken":self.userToken}
        self.session.post(url,json=data);

        url = "http://org.xjtu.edu.cn/openplatform/toon/auth/generateTicket"
        params = {
            'personToken':self.userToken,
            'empNo':self.username
        }
        r = self.session.get(url,params=params,headers={
                "secretKey":"18a9d512c03745a791d92630bc0888f6"
            })
        ticket = json.loads(r.text)['data']['ticket']
        return ticket

    
    def search(self,mode):
        '''
        mode = 0 全局扫描  mode = 1 单日查询（只查看第五天场地） mode=2 单日查询,指定场地
        无需登录即可搜索
        '''
        #为精简search内容，将查询前的准备放在login中
        url = "http://org.xjtu.edu.cn/workbench/member/appNew/getOauthCode"
        params = {
            "userId":self.userId,
            "orgId":self.orgId,
            "appId":'760',
            "state":'2222',
            "redirectUri":'http://202.117.17.144:8080/web/index.html?userType=1',
            "employeeNo":self.username,
            "personToken":self.userToken
        }
        r = self.session.get(url,params=params)
        # r = self.session.get('http://202.117.17.144/index.html') #http://202.117.17.144/index.html
        # print("202.117.17.144",r.status_code)
        if r.status_code==200:
            t = datetime.datetime.fromtimestamp(int(time.time()), tz).strftime('%Y-%m-%d %H:%M:%S %Z%z')

            print(f"欢迎进入体育场馆预定系统{t}")

        #返回值为html有可用信息
        url_BMT1 = 'http://202.117.17.144/product/show.html?id=' +self.platid;
        r = self.session.get(url_BMT1);
        print("id=",self.platid,r.status_code);

        #-----------------------------获取场地信息-------------------------------
        #五天的全部场地信息，用字典存储
        AllPlatTable = {};
        today = datetime.datetime.fromtimestamp(int(time.time()), tz).today()

        start  = 0 if mode == 0 else 4;
        for i in  range(start,5):
            tomorrow = today + datetime.timedelta(days=i)
            date = tomorrow.strftime("%Y-%m-%d")
            if mode == 2:
                if self.date == '':
                    print('请指定日期')
                    return 
                else:
                    date = self.date
            t =int(round(time.time()*1000));
            param = {
                's_date': date,
                'serviceid': self.platid
            }
            url_getokinfo= 'http://202.117.17.144:8080/web/product/findOkArea.html';
            # http://202.117.17.144/product/findOkArea.html
            r = self.session.get(url_getokinfo,params=param,allow_redirects=False)
    
            content = r.text;
            pattern = r'"id":([0-9]+).*?"sname":"(场地[\d]+).*?"status":([\d]).*?"time_no":"([0-9:-]+).*?"stockid":([0-9:-]+)';
            plat = re.findall(pattern,content,re.S)
            print(date,'可选场地信息:')
            PlatTable = [];                              #收集某一天的全部空场信息
            for i in plat:
                if(i[2]=='1'):
                    print(i)
                    PlatTable.append(i)
            if not PlatTable:
                print('无空余场地')
            AllPlatTable[date] = PlatTable;   

        self.allplat = AllPlatTable

    def select(self,priority:list,mode) -> list:
        '''
        从已查询列表中按优先级次序选择场地,返回一个场地信息
        priority:按24h制的小时优先级列表,20表示预约20；00——21:59的场地
        实例['20','21','19','09','16']
        '''
        if mode:
            if self.platid == '41':
                plat_num = int(1 + 9*random())
            else:
                plat_num = int(1 + 11*random())
        today = datetime.datetime.fromtimestamp(int(time.time()), tz).today()
        date_list = []
        if mode == 0:
            for i in  range(0,5):
                date = (today + datetime.timedelta(days=i)).strftime("%Y-%m-%d")
                date_list.append(date)
        elif mode == 1:
            date =   (today + datetime.timedelta(days=4)).strftime("%Y-%m-%d")
            date_list.append(date)
        elif mode == 2:
            date = self.date
            date_list.append(date)
        
        for i,date in enumerate(date_list):
            DayPlatTable =self.allplat[date]
            for stime in priority:
                for plat in DayPlatTable:
                    if mode:
                        # if(plat[3][0:2] == time):
                        if(plat[3][0:2] == stime and plat[1] == '场地'+str(plat_num)):
                            res= list(plat)
                            res.append(date)
                            return res
                    else:
                        if(plat[3][0:2] == stime ):
                            res= list(plat)
                            res.append(date)
                            return res
        return []
        
    def book(self,isEmail:bool, selectplat, InfoList:list = [],thread_id=''):
        '''
        isEmail 是否发送邮件
        selectplat 选择的场地
        InfoList 为邮箱配置的端口密码等
        '''
        print("正在预定,请稍后…………")
        if not selectplat:
            print("无符合条件的场地")
            return 0,'null','null'
        #--------------------------------------------------
        # self.login_again();
        for i in range(0,11):
            num = str(random());
            url_yzm ='http://202.117.17.144:8080/web/login/yzm.html?' + num;
            r = self.session.get(url_yzm)
            if r.status_code == '404':
                return -1,'yzm请求有误'
            current_path = os.getcwd()
            with open(current_path + '/BadmintonXJTU/project/main/yzm/image/yzm'+thread_id+'.jpg','wb') as f:
                f.write(r.content)
            yzm = ocr(current_path + '/BadmintonXJTU/project/main/yzm/image/yzm'+thread_id+'.jpg',5,3)
            if len(yzm) != 4:
                continue

            url_tobook = 'http://202.117.17.144:8080/web/order/tobook.html';
            data = {
                'param': json.dumps({
                    "stockdetail": {
                        selectplat[4]: selectplat[0]
                    }, 
                    "yzm":yzm,
                    "address":self.platid}).replace(' ',''),
                'json':'true'
            }
            headers ={'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8'};
            r = self.session.post(url_tobook,data=data,allow_redirects=False);
            print(r.text)
            if r.status_code == '404':
                print('404错误')
            msg = json.loads(r.text)['message']
            if msg == '验证码错误':
                continue
            elif msg == "USERNOTLOGINYET":
                self.login()
            elif msg == '未支付':
                orderId = json.loads(r.text)['object']['order']['orderid']
                print('预定成功')
                if isEmail and InfoList:
                    platName = '  一楼  'if(self.platid =='41')else'  三楼 '
                    email_inf = '您的羽毛球场预约小助手已为您预约成功了\n场地信息:\n'+ \
                        selectplat[-1] + platName +selectplat[1] + '  ' + selectplat[3];
                    email(email_inf,InfoList[0])
                
                return 1,orderId,selectplat[3][:2]     #True success
            else:
                pass
        return 0,'null','null'

        # orderid = re.findall(r'"orderid":"([\d]*?)"',r.text)[0]
        # print("orderid",orderid);
        # return orderid

    def buy(self,orderid,querypwd):
        '''
        orderid 为预定后返回的订单号  querypwd为一卡通查询密码
        '''
        print("正在购买，请稍后…………")
        url_showpay ='http://202.117.17.144:8080/web/pay/paymentPlatform/showpay.html'
        param = {
            'orderid': orderid,
            'payid': '6'
        }
        r =self.session.get(url_showpay,params=param);
        # print("url_payplat",r.status_code)

        # tranamt account sno toaccount thirdsystem thirdorderid ordertype sign orderdesc praram1 thirdurl
        param_for_next = re.findall(r'name="(.*?)".*?value="(.*?)"',r.text)
        data={};
        for p in param_for_next:
            data[p[0]] = p[1]
        url_creatorder ='http://202.117.1.244:9001/Order/CreateOrder';
        r = self.session.post(url_creatorder,data=data)
        print("第三方支付系统已唤起",r.status_code)
        #得到信息中有orderid_2
        pattern = r'\w[0-9]{28}'
        orderid_2 = re.search(pattern,r.text,re.S).group()
        # print("orderid_2",orderid_2)

        url_CommonMobilePay ='http://202.117.1.244:9001/Pay/CommonMobilePay'
        data={
            'orderid': orderid_2,
            'payid': '1',
            'param1':'000',
            'paytype':'phonep'
        }
        r = self.session.post(url_CommonMobilePay,data=data, allow_redirects=False)
        print('Pay',r.status_code)
        if r.status_code==200:
            print("支付成功")
            return True
        else:
            return False
    
def bmt_for_winmenu(un,pwd,platid,mode,date=''):
    ydjd = YiDongJiaoDa(un,pwd,platid,date);
    ydjd.search(mode);
    return ydjd.allplat

def bmt_for_thread(ydjd:YiDongJiaoDa, userInfo,mode,thread_id,isEmail):
    '''为线程创建的调用接口。
    mode：0表示检漏模式；1表示定时抢场地模式
    '''
    if mode == 1:
        ydjd.login()
        nowTime = datetime.datetime.fromtimestamp(int(time.time()), tz)
        print(f"登录后的时间：{nowTime}")
        # t = (datetime.datetime.now() + datetime.timedelta(seconds=5)).strftime('%H:%M:%S') 
        targetTime = datetime.datetime.strptime("08:40:00","%H:%M:%S").replace(tzinfo=pytz.timezone('Asia/Shanghai')) #"08:40:00"
        print(f"目标时间：{targetTime}")
        seconds = (targetTime-nowTime).seconds
        print(f"休眠时间：{seconds}s")
        time.sleep(seconds);
        circulation_num = 5
        plat_booked_num = 0
        while (circulation_num>0 and plat_booked_num<=2 ):
            try:
                ydjd.search(mode)
                selectplat = ydjd.select(userInfo['priority'],mode)
                if selectplat:
                    ydjd.login_again()
                    status,id,sTime = ydjd.book(isEmail,selectplat,userInfo['emailConfig'],thread_id);
                    if status == 1:
                        plat_booked_num += 1;
                        userInfo['priority'].remove(sTime)
                        ydjd.buy(id,userInfo['searchPwd']);
            except Exception as e:
                print(e)
            time.sleep(1);
            circulation_num -= 1;
        return
    else:        
        #由于定时任务是相互独立的，在抢到一定数量的场地之后应当及时关停程序，否则会无休止地执行下去
        # try:
        ydjd.search(mode)
        selectplat = ydjd.select(userInfo['priority'],mode)
        print(selectplat)
        if selectplat:
            status,id = ydjd.book(True,selectplat,userInfo['emailConfig']);
            if status == 1:
                confirm = input("Input OK to buy: ")
                if confirm == "OK":
                    ydjd.buy(id);
                    return True
        # except Exception as e:
        #     print(e)
        return False

if __name__ == '__main__':
    userInfo = userInfoRead();
    userInfo['priority'].remove("19")
    pass
    ydjd = YiDongJiaoDa(userInfo['username'],userInfo['pwd'],'41');

    mode = 0
    ticket = ydjd.login()
    print('ticket:',ticket)
    if type(ticket) is not str:
        exit(-1);

    ydjd.search(mode);
    selectplat = ydjd.select(userInfo['priority'],mode)
    print(selectplat)
    id = ydjd.book(True,selectplat,userInfo['emailConfig']);

    ydjd.platid = '42'
    ydjd.search(mode);
    selectplat = ydjd.select(userInfo['priority'],mode)
    print(selectplat)
    id = ydjd.book(True,selectplat,userInfo['emailConfig']);
    

    # if id != 'null':
    #     ydjd.buy(id,userInfo['searchPwd']);

    
   

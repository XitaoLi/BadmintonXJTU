#!/usr/bin/env python3
#coding:utf-8
import base64
import datetime
from email.mime.text import MIMEText
import json
import re
import smtplib
import time
from random import random
import traceback
import requests
import os
import pytz as pytz
from yzm.slider_yzm import build_post
from SpiderAgency import ua_change
import logging
import globalLogger
tz = pytz.timezone('Asia/Shanghai') 

def userInfoRead():
    current_path = os.getcwd()
    with open(current_path + '/docs/user_config.json','r') as f:
      return json.load(f)

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
    msg_From = info["from"]
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
    smtp.quit()

class YiDongJiaoDa(object):
    def __init__(self,username,passward,PlatFlag:str,date='') -> None:
        '''
        username:登录平台用户名；passward：登录平台密码
        PlatFlag: '41' 一楼 '42'三楼
        date：要预定的日期，格式为2022-06-11
        '''
        self.username = username
        self.passward = passward
        self.session = requests.session()
        # self.session.keep_alive = False
        self.session.headers['User-Agent'] = ua_change()
        globalLogger.logger.info("Random select UA header:%s",self.session.headers['User-Agent'])
        # print('随机配置UA信息',self.session.headers['User-Agent'])
        #41 一楼 42 三楼
        self.platid = PlatFlag
        self.allplat = {}
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
        """待机时间过长会有一个再次验证的过程"""
        url = 'http://org.xjtu.edu.cn/openplatform/toon/private/userLoginByToken'
        data={"userToken":self.userToken}
        self.session.post(url,json=data)

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

            globalLogger.logger.info(f"Now time: {t} Searching... ")

        #返回值为html，有可用信息
        url_BMT1 = 'http://202.117.17.144/product/show.html?id=' +self.platid
        r = self.session.get(url_BMT1)
        # globalLogger.logger.debug(f"id={self.platid} {r.status_code}")

        #-----------------------------获取场地信息-------------------------------
        #五天的全部场地信息，用字典存储
        AllPlatTable = {}
        today = datetime.datetime.fromtimestamp(int(time.time()), tz).today()

        start  = 0 if mode == 0 else 4
        for i in  range(start,5):
            tomorrow = today + datetime.timedelta(days=i)
            date = tomorrow.strftime("%Y-%m-%d")
            if mode == 2:
                if self.date == '':
                    globalLogger.logger.error("No special day appointed in mode 2.")
                    return 
                else:
                    date = self.date
            t =int(round(time.time()*1000))
            param = {
                's_date': date,
                'serviceid': self.platid
            }
            url_getokinfo= 'http://202.117.17.144:8080/web/product/findOkArea.html'
            # http://202.117.17.144/product/findOkArea.html
            r = self.session.get(url_getokinfo,params=param,allow_redirects=False)
    
            content = r.text
            pattern = r'"id":([0-9]+).*?"sname":"(场地[\d]+).*?"status":([\d]).*?"time_no":"([0-9:-]+).*?"stockid":([0-9:-]+)'
            plat = re.findall(pattern,content,re.S)
            PlatTable = []                              #收集某一天的全部空场信息
            for i in plat:
                if(i[2]=='1'):
                    print(i)
                    PlatTable.append(i)
            if not PlatTable:
                globalLogger.logger.info(f"date:{date} No court available.")
            else:
                tmp_str = "\n".join([str(x) for x in PlatTable])
                globalLogger.logger.info(f"date:{date} selectable courts:\n{tmp_str}")
            AllPlatTable[date] = PlatTable   

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
                        if(plat[3][0:2] == stime):
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
        # print("正在预定,请稍后…………")
        if not selectplat:
            globalLogger.logger.info("No courts meet the requirement.")
            return 0,'null','null'
        #--------------------------------------------------
        # self.login_again()
        for i in range(0,10):

            # get figure
            url_yzm ="http://202.117.17.144:8080/gen"
            r = self.session.get(url_yzm)
            response_json = r.json()
            start_idx = len("data:image/jpeg;base64,")
            backgroundImage = response_json["captcha"]["backgroundImage"][start_idx:]
            bgImg = base64.b64decode(backgroundImage)
            str = time.asctime()
            with open("yzm/img/bgImg.png",'wb') as f:
                f.write(bgImg)
            start_idx = len("data:image/png;base64,")
            sliderImage = response_json["captcha"]["sliderImage"][start_idx:]
            sldImg = base64.b64decode(sliderImage)
            with open("yzm/img/sliderImg.png",'wb') as f:
                f.write(sldImg)
            
            bg_shape = [response_json["captcha"]["backgroundImageWidth"] , response_json["captcha"]["backgroundImageHeight"]]
            slider_shape = [response_json["captcha"]["sliderImageWidth"] , response_json["captcha"]["sliderImageHeight"]]
            if bg_shape[1] != slider_shape[1]:
                slider_shape[1] = bg_shape[1]
            show_shape = (260,159)
            k = show_shape[1]/bg_shape[1]
            # show_shape = bg_shape
            # k = 1
            _yzm = build_post(show_shape,(round(slider_shape[0]*k),show_shape[1]),k)
            id = response_json["id"]
            yzm = json.dumps(_yzm) + f"synjones{id}synjoneshttp://202.117.17.144:8071"
            url_tobook = 'http://202.117.17.144:8080/web/order/tobook.html'
            data = {
                "param": json.dumps({
                    "stockdetail": {
                        selectplat[4]: selectplat[0]
                    }, 
                    "venueReason":"","fileUrl":"","remark":"",
                    "address":self.platid}),
                "yzm":yzm,
                "json":'true'
            }
            r = self.session.post(url_tobook,data=data,allow_redirects=False)
            globalLogger.logger.debug(r.text)
            if r.status_code == '404':
                globalLogger.logger.error('404 error')
            msg = json.loads(r.text)['message']
            if 'message' not in r.text:
                globalLogger.logger.info("r.text")
                assert json.loads(r.text)['message'] , "请求有误，msg字段未知"
            if msg == '验证码有误！':
                globalLogger.logger.info("Retry slider auth code recognition.")
                continue
                
            elif msg == "USERNOTLOGINYET":
                self.login()
            elif "已过有效期" in msg:
                globalLogger.logger.error("Auth code is out of validity.")
                pass
            elif msg == '未支付':
                orderId = json.loads(r.text)['object']['order']['orderid']
                globalLogger.logger.info("Successful for reservation.")
                if isEmail and InfoList:
                    platName = '  一楼  'if(self.platid =='41')else'  三楼 '
                    email_inf = '您的羽毛球场预约小助手已为您预约成功了\n场地信息:\n'+ \
                        selectplat[-1] + platName +selectplat[1] + '  ' + selectplat[3]
                    email(email_inf,InfoList[0])
                    globalLogger.logger.info("Successful for sending the email.")
                
                return 1,orderId,selectplat[3][:2]     #True success
            else:
                pass
        return 0,'null','null'

        # orderid = re.findall(r'"orderid":"([\d]*?)"',r.text)[0]
        # print("orderid",orderid)
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
        r =self.session.get(url_showpay,params=param)
        # print("url_payplat",r.status_code)

        # tranamt account sno toaccount thirdsystem thirdorderid ordertype sign orderdesc praram1 thirdurl
        param_for_next = re.findall(r'name="(.*?)".*?value="(.*?)"',r.text)
        data={}
        for p in param_for_next:
            data[p[0]] = p[1]
        url_creatorder ='http://202.117.1.244:9001/Order/CreateOrder'
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
    

def bmt_for_thread(ydjd:YiDongJiaoDa, userInfo,mode,thread_id,isEmail):
    '''为线程创建的调用接口。
    mode：0表示检漏模式；1表示定时抢场地模式
    '''
    if mode == 1:
        ydjd.login()
        now_time = datetime.datetime.fromtimestamp(int(time.time()), tz)
        globalLogger.logger.info(f"登录后的时间：{now_time}")
        today = now_time.today()
        # thread 控制在8：39传入，因此无需判断targetday
        # if int(now_time.hour) >= 8:
        #     target_day = today + datetime.timedelta(days=1)
        # else:
        target_day = today
        target_time = datetime.datetime(target_day.year,target_day.month,target_day.day,8,40,0,0,now_time.tzinfo)
        globalLogger.logger.info(f"目标时间：{target_time}")
        seconds = (target_time - now_time).seconds
        globalLogger.logger.info(f"休眠时间：{seconds}s")
        time.sleep(seconds)
        circulation_num = 5
        plat_booked_num = 0
        while (circulation_num>0 and plat_booked_num<=2 ):
            try:
                ydjd.search(mode)
                selectplat = ydjd.select(userInfo['priority'],mode)
                globalLogger.logger.info("选择的场地是："+str(selectplat))
                if selectplat:
                    ydjd.login_again()
                    status,id,sTime = ydjd.book(isEmail,selectplat,userInfo['emailConfig'],thread_id)
                    if status == 1:
                        plat_booked_num += 1
                        userInfo['priority'].remove(sTime)
                        ydjd.buy(id,userInfo['searchPwd'])
            except Exception as e:
                globalLogger.logger.error(e)
                globalLogger.logger.error("\n" + traceback.format_exc())
            time.sleep(1)
            circulation_num -= 1
        return
    else:        
        #由于定时任务是相互独立的，在抢到一定数量的场地之后应当及时关停程序，否则会无休止地执行下去
        try:
            ydjd.search(mode)
            selectplat = ydjd.select(userInfo['priority'],mode)
            globalLogger.logger.info("选择的场地是：" + str(selectplat))
            if selectplat:
                status,id,_a = ydjd.book(True,selectplat,userInfo['emailConfig'])
                if status == 1:
                    confirm = input("Input OK to buy: ")
                    if confirm == "OK":
                        ydjd.buy(id)
                        exit(0)
                        return True
        except Exception as e:
            globalLogger.logger.error(e)
            globalLogger.logger.error("\n" + traceback.format_exc())

        #     print(e)
        return False

if __name__ == '__main__':
    ### 以下程序仅用来debug，真正的入口在thread程序里
    globalLogger._init()
    userInfo = userInfoRead()
    userInfo['priority'].remove("19")
    pass
    ydjd = YiDongJiaoDa(userInfo['username'],userInfo['pwd'],'41')

    mode = 0
    ticket = ydjd.login()
    # print('ticket:',ticket)
    if type(ticket) is not str:
        exit(-1)

    # ydjd.search(mode)
    # selectplat = ydjd.select(userInfo['priority'],mode)
    # print(selectplat)
    # id = ydjd.book(True,selectplat,userInfo['emailConfig'])

    ydjd.platid = '41'
    ydjd.search(mode)
    selectplat = ydjd.select(userInfo['priority'],mode)
    print(selectplat)
    id = ydjd.book(True,selectplat,userInfo['emailConfig'])
    

    # if id != 'null':
    #     ydjd.buy(id,userInfo['searchPwd'])

    
   

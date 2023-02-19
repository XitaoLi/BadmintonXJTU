
import copy
import threading
from time import sleep
import datetime
from PlayBadminton import *
import schedule
import logging

import globalLogger

def MainBook():
    userInfo = userInfoRead()
    globalLogger.logger.info("Finish loading user info.")

    mode = userInfo["mode"]       #mode为2还需要在Line38传入指定日期
    floor = userInfo["floor"]   #一楼'41' 三楼'43'
    isEmail = userInfo["isEmail"] #是否发送邮件
    date = userInfo["date"] # 格式为2023-2-19
    
    start_time = datetime.datetime.strptime("08:29:00","%H:%M:%S") #08:40:00
    tz = pytz.timezone('Asia/Shanghai')
    for i in tz._tzinfos:
        if i[2] == 'CST':
            dt = i[0]
    start_time_tz = (start_time - dt).strftime('%H:%M:%S') 
    # start_time = (datetime.datetime.now() + datetime.timedelta(seconds=2)).strftime('%H:%M:%S') 
    if mode == 1:
        sub_thread = []
        ydjd = YiDongJiaoDa(userInfo['username'],userInfo['pwd'],floor);
        for i in range(0,1):
            globalLogger.logger.info("Start registering for the thread %s.",2*i+1)
            sub_thread.append( threading.Thread(target = bmt_for_thread,args=(ydjd,userInfo,mode,str(i)+'-1',isEmail)) )
            # sub_thread.append( threading.Thread(target = bmt_for_thread,args=(ydjd2,userInfo,mode,str(i)+'-2')) )
            # sub_thread.append( threading.Thread(target = test) )
        schedule_break_flag = False
        def job_that_executes_once():
            # globalLogger.logger.debug("hello Beijing Time")
            for i in range(0,1):
                sub_thread[i].start()
                sleep(10)   
            return schedule.CancelJob
        schedule.every().day.at(start_time_tz).do(job_that_executes_once)
        while True:
            schedule.run_pending()
            sleep(1)
    else:
        ydjd = YiDongJiaoDa(userInfo['username'],userInfo['pwd'],floor);
        ydjd.login()
        ydjd2 = copy.deepcopy(ydjd)
        ydjd2.platid = '42'
        schedule.every(5).seconds.do(bmt_for_thread,ydjd=ydjd,userInfo=userInfo,mode=mode,thread_id = '1-1',isEmail=isEmail)
        schedule.every(120).seconds.do(bmt_for_thread,ydjd=ydjd2,userInfo=userInfo,mode=mode,thread_id = '1-2,',isEmail =isEmail)
        while 1:
            schedule.run_pending()
            sleep(1)
if __name__ == "__main__":
    globalLogger._init()
    MainBook()
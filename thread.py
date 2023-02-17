
import copy
import threading
from time import sleep
from PlayBadminton import *
import schedule
def MainBook():
    # def test():
    #     print('rtest')
    userInfo = userInfoRead()
    
    # user parameter
    mode = 1       #mode为2还需要在Line38传入指定日期
    floor = '41'   #一楼'41' 三楼'43'
    isEmail = True #是否发送邮件
    
    start_time = "08:39:00" #08:40:00
    # start_time = (datetime.datetime.now() + datetime.timedelta(seconds=2)).strftime('%H:%M:%S') 
    if mode:
        sub_thread = []
        ydjd = YiDongJiaoDa(userInfo['username'],userInfo['pwd'],floor);
        for i in range(0,1):
            print("正在注册线程",2*i+1,'--------------')
            sub_thread.append( threading.Thread(target = bmt_for_thread,args=(ydjd,userInfo,mode,str(i)+'-1',isEmail)) )
            # sub_thread.append( threading.Thread(target = bmt_for_thread,args=(ydjd2,userInfo,mode,str(i)+'-2')) )
            # sub_thread.append( threading.Thread(target = test) )
        schedule_break_flag = False
        def schedule_thread():
            global schedule_break_flag 
            schedule_break_flag= True
            for i in range(0,1):
                sub_thread[i].start()
                sleep(10)   
        schedule.every().day.at(start_time).do(schedule_thread)
        while not schedule_break_flag:
            schedule.run_pending()
            sleep(1)
    else:
        ydjd = YiDongJiaoDa(userInfo['username'],userInfo['pwd'],floor);
        ydjd.login()
        ydjd2 = copy.deepcopy(ydjd)
        ydjd2.platid = '42'
        schedule.every(120).seconds.do(bmt_for_thread,ydjd=ydjd,userInfo=userInfo,mode=mode,thread_id = '1-1',isEmail=isEmail)
        schedule.every(120).seconds.do(bmt_for_thread,ydjd=ydjd2,userInfo=userInfo,mode=mode,thread_id = '1-2,',isEmail =isEmail )
        while 1:
            schedule.run_pending()
            sleep(1)
if __name__ == "__main__":
    MainBook()
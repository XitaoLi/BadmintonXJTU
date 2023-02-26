
import datetime
import random
import cv2
import time
import pytz
operate_time = 2023 #milliseconds
tz = pytz.timezone('Asia/Shanghai') 
def identify_gap(bg,sld):
    """来源：https://blog.csdn.net/zhangzeyuaaa/article/details/119508407，在此基础上做了修改
    """
    bg_img = cv2.imread(bg)
    sld_img = cv2.imread(sld)[:bg_img.shape[0],:]
    bg_img = cv2.cvtColor(bg_img, cv2.COLOR_BGR2GRAY)
    sld_img = cv2.cvtColor(sld_img, cv2.COLOR_BGR2GRAY)
    ret,bg_img=cv2.threshold(bg_img, 127, 255, cv2.THRESH_BINARY)
    ret,sld_img=cv2.threshold(sld_img, 127, 255, cv2.THRESH_BINARY)
    bg_edge = cv2.Canny(bg_img, 100, 200)
    sld_edge = cv2.Canny(sld_img, 100, 200)

    # 缺口匹配
    res = cv2.matchTemplate(bg_edge, sld_edge , cv2.TM_CCOEFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res) # 寻找最优匹配
    tl = max_loc # 左上角点的坐标

    # # 绘制方框
    # th, tw = sld_img.shape[:2] 
    # tl = max_loc 
    # br = (tl[0]+tw,tl[1]+th)
    # cv2.rectangle(bg_img, tl, br, (0, 0, 255), 2) # 绘制矩形
    # cv2.imwrite('out.jpg', bg_img) # 保存在本地
    # # tl[0]恰好为滑动距离
    return tl[0]


def build_track(k):
    real_start_time = 170
    tracklist = [{"x":0,"y":0,"type":"down","t":real_start_time}]

    # The function of y with respect to x is: y = 0.1 x + int(2*random()-1)
    # The function of x with respect to t is: x = a*(t-b)^2 +c
    xm = round(identify_gap('yzm/img/bgImg.png','yzm/img/sliderImg.png') * k)
    tm = operate_time
    a = - xm/tm**2
    for t in range(real_start_time,tm,21):
        x = int(a*(t-tm)**2 +xm)
        y = int(0.1*x + int(2*random.random()-1))
        tracklist.append({"x":x,"y":y,"type":"move","t":t})
    tracklist.append({"x":xm,"y":y,"type":"up","t":tm})
    # print(tracklist)
    return tracklist
def build_post(bg_shape,slider_shape,k):
    now_time = datetime.datetime.fromtimestamp(int(time.time()), tz)
    start_time = now_time - datetime.timedelta(microseconds = operate_time*1000)
    start_slide_time = start_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] +'Z'
    end_slide_time = now_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] +'Z'
    data = {
        "bgImageWidth": bg_shape[0],
        "bgImageHeight": bg_shape[1],
        "sliderImageWidth": slider_shape[0],
        "sliderImageHeight": slider_shape[1],
        "startSlidingTime": start_slide_time,
        "entSlidingTime": end_slide_time,
        "trackList":build_track(k)
    }
    return data

# print(identify_gap('yzm/img/bgImg.png','yzm/img/sliderImg.png'))
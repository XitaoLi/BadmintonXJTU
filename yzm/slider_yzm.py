
import datetime
import random
import cv2

operate_time = 2023 #milliseconds

def identify_gap(bg,tp):
    '''
    bg: 背景图片
    tp: 缺口图片
    '''
    bg_img = cv2.imread(bg)
    tp_img = cv2.imread(tp)
    bg_edge = cv2.Canny(bg_img, 100, 200)
    tp_edge = cv2.Canny(tp_img, 100, 200)
    bg_pic = cv2.cvtColor(bg_edge, cv2.COLOR_GRAY2RGB)
    tp_pic = cv2.cvtColor(tp_edge, cv2.COLOR_GRAY2RGB)

    # 缺口匹配
    res = cv2.matchTemplate(bg_pic, tp_pic, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res) # 寻找最优匹配
    tl = max_loc # 左上角点的坐标

    # tl[0]恰好为滑动距离
    return tl[0]


def build_track():
    real_start_time = 170
    tracklist = [{"x":0,"y":0,"type":"down","t":real_start_time}]

    # The function of y with respect to x is: y = 0.1 x + int(2*random()-1)
    # The function of x with respect to t is: x = a*(t-b)^2 +c
    xm = identify_gap('resource/bgImg.png','resource/sliderImg.png')
    tm = operate_time
    a = - xm/tm**2
    for t in range(real_start_time,tm,21):
        x = int(a*(t-tm)**2 +xm)
        y = int(0.1*x + int(2*random.random()-1))
        tracklist.append({"x":x,"y":y,"type":"move","t":t})
    tracklist[-1]["type"] = "up"
    # print(tracklist)
    return tracklist
def build_post():
    now_time = datetime.datetime.now()
    start_time = now_time - datetime.timedelta(microseconds = operate_time*1000)
    start_slide_time = start_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] +'Z'
    end_slide_time = now_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] +'Z'
    data = {
        "bgImageWidth": 260,
        "bgImageHeight": 0,
        "sliderImageWidth": 0,
        "sliderImageHeight": 159,
        "startSlidingTime": start_slide_time,
        "entSlidingTime": end_slide_time,
        "trackList":build_track
    }
    sync = f"synjones{id}synjoneshttp://202.117.17.144:8071"
    return data

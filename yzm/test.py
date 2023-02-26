import base64
import json,time
from slider_yzm import *
import requests
"""
本程序用于测试cv识别滑动验证码的准确性，注意"http://202.117.17.144:8071/gen"需要在校园网环境下请求
"""
epoch = 30
acc = {'total':0,"abnormal":0} #abnormal是指slider height与background height不等
abnormal_count = 0
while epoch:
    epoch -= 1
    url = "http://202.117.17.144:8071/gen"
    r = requests.get(url).json()
    response_json  = r
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
    if r["captcha"]["backgroundImageWidth"] != 590:
        abnormal_count +=1
    id = r["id"]
    bg_shape = [r["captcha"]["backgroundImageWidth"] , r["captcha"]["backgroundImageHeight"]]
    slider_shape = [r["captcha"]["sliderImageWidth"] , r["captcha"]["sliderImageHeight"]]
    if bg_shape[1] != slider_shape[1]:
        slider_shape[1] = bg_shape[1]
    show_shape = (260,159)
    k = show_shape[1]/bg_shape[1]
    # show_shape = bg_shape
    # k = 1
    yzm = build_post(show_shape,(round(slider_shape[0]*k),show_shape[1]),k)
    rp = requests.post("http://202.117.17.144:8071/check",params={'id':id},json=yzm)
    if rp.text == "true":
        acc["total"] += 1
        if r["captcha"]["backgroundImageWidth"] != 590:
            acc['abnormal'] +=1
    else:
        # print("error")
        pass
print(f"accuracy total:%.3f"%(acc["total"]/30))
print(f"accuracy abnormal:%.3f"%(acc["total"]/30))
## 项目说明
本项目可实现西安交通大学兴庆校区羽毛球场馆的预约，提供全局扫描以及定时抢场两种功能。

This project can reserve badminton venues in Xingqing Campus of XJTU, and provide two basic functions: global scanning and timing competition.

## 环境
项目依赖库已打包好，执行`pip install -r requirements.txt`可快速添加依赖项

## 参数设置
主程序入口为 [threat](project/main/thread.py)，提供三种功能：
1. mode = 0 全局扫描  
2. mode = 1 抢场（只查看第五天场地） 
3. mode = 2  单日扫描,指定场地

可在`threat->user->parameter`中更改可选项。或者在[PlayBadminton.py](project/main/PlayBadminton.py)中进行更为详细的设置。

在文件[user_config.json](docs/user_config.json)，并按以下格式填写帐密、查询密码、预约偏好等信息，此部分涉及敏感信息并未上传云端
```json
//文件不能有中文注释,此处注释只为帮助规范数据格式
{
  "username":"****",
  "pwd":"******",
  "searchPwd":"******", //六位校园卡查询密码
  "priority":["19","18","20","10","11","15","16","09"], //按24h制表示的小时优先级列表,20表示预约20；00——21:59的场地
  "emailConfig":[
    {
      "from":"******@qq.com",
      "to":"*****@qq.com",
      "smtpServer":"smtp.qq.com",
      "port":"****",
      "AuthorizationCode":"******" //stmp服务授权码
    }
  ]
}
```

## RUN
 Linux 执行``nohup python -u BadmintonXJTU/project/main/thread.py >> my.log 2>&1 &``即可后台运行

## 分支说明
- **Linux版本**：推荐使用linux-release分支，需要部署在服务器上
- **Win版本**：mobiledev分支基于移动端接口，注意程序运行期间需要确保userToken不变，因此程序运行后手机端需要重新登录（Win版本需要电脑24小时不停机，由于实用性问题已放弃维护）
- dev分支基于网页版接口，但2022.9版本由于学校接口变更，该版本已废弃


## 文件地图
```bash
BadmintonXJTU
│  .gitignore
│  README.md
│  tree.txt
|  requirements.txt
│  winmenu.exe #封装后的查询可视化界面
│  winmenu.py
├─bin
├─docs
│      DevLog.md           #开发日志
│      user_config.json
│      
└─project
    ├─main
    │  │  PlayBadminton.py
    │  │  thread.py
    │  │  ua.py
    │  │  
    │  └─yzm
    │      │  accuary.txt      #不同方法输出的准确性
    │      │  get_yzm_database.py
    │      │  ocr.py
    │      │  testAns.txt
    │      │  
    │      ├─image
    │      │      yzm.jpg
    │      │      yzmres.png
    │      │      
    │      ├─imagedata          #验证码样本库
    │      └─imageProcessed    
    ├─resource
    |       IPpond.txt         
    └─test
            aes.js
            JsToPy.py
            test.py
```   
## 注意事项
本程序仅供学习交流使用，切勿用于商业用途！


如果觉得不错，麻烦点个star支持一下吧
---
@Copyright Ton


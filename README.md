## 项目说明
本项目为西安交通大学兴庆校区羽毛球场馆预约脚本，提供全局扫描、单日扫描、定时抢场三种功能。

This project can reserve badminton venues in Xingqing Campus of XJTU, and provide two basic functions: global scanning and timing competition.

## 环境配置
项目依赖库已打包好，执行`pip install -r requirements.txt`可快速添加依赖项

## 参数设置
所有参数集成在[user_config.json](docs/user_config.json)配置文件中，按以下格式填写帐密、查询密码、预约偏好等信息，此部分涉及敏感信息并未上传云端。

工作模式
1. mode = 0 全局扫描  
2. mode = 1 抢场（只查看第五天场地） 
3. mode = 2  单日扫描,指定场地




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
  ],
  "mode":0, //工作模式
  "floor": "41", //41为1楼，42为三楼
  "isEmail": 1,
  "date":"" //在模式2下必须指定日期，格式为2023-01-01
}
```
Note:可在[PlayBadminton.py](PlayBadminton.py)中更改运行逻辑以进行细粒度的设置。
## RUN
 1. nohug. Linux 执行``nohug python -u thread.py``即可后台运行
 2. tmux后台运行. 

 ## 结果示例
 <img src="https://www.notion.so/image/https%3A%2F%2Fs3-us-west-2.amazonaws.com%2Fsecure.notion-static.com%2Fed88453c-82b1-4f40-85a8-5b60cf16f364%2FUntitled.png?table=block&spaceId=d7dc1ab1-646a-42b9-a1f8-81af0a705957&id=24945a1d-e2a3-470b-8d1d-13b85d75bfd2&width=2000&userId=be755080-78ce-4748-92c4-807604f56b10&cache=v2" alt = "结果显示" width="50%" style="margin:0 auto"/>

## 分支说明
- **Linux版本**：推荐使用linux-release分支，需要部署在服务器上
- **Win版本**：mobiledev分支基于移动端接口，注意程序运行期间需要确保userToken不变，因此程序运行后手机端需要重新登录（Win版本需要电脑24小时不停机，由于实用性问题已放弃维护）
- dev分支基于网页版接口，但2022.9版本由于学校接口变更，该版本已废弃


## 文件地图
```bash
.
├── PlayBadminton.py
├── README.md
├── SpiderAgency.py
├── docs
│   ├── DevLog.md
│   └── user_config.json
├── requirements.txt
├── thread.py
├── tree.txt
└── yzm
    ├── analysis.ipynb
    ├── getMouse.py
    └── slider_yzm.py
```   
## 注意事项
本程序仅供学习交流使用，切勿用于商业用途！

如果觉得不错，麻烦点个star支持一下吧
---
@Copyright Ton


## 2022.9.17
重启羽毛球场馆预约脚本开发项目，在课程作业的基础上进行更深入的设计（主要是无聊）。

主要任务：
1. 信息脱敏
2. 解决第二次访问https://cas.xjtu.edu.cn/login 出现的需要再次输入帐密的问题
## 2022.9.18
优化验证码部分的逻辑（cv水太深了）
## 2022.9.19
feat：多线程抢场地。
bug：
1. 某个thread成功后未能结束程序。
2. readme文档待更新
3. 捡漏模式待开发
   
**一些总结**：
1. gitignore 只在代码未提交到本地仓库前有效,一旦admit后gitignore便无法追踪
2. schedule用于简单调度效果不好，不如sleep简单,或者说没有搞清楚schedule的应用场景

3. 发现win cmd自带的一个方便的功能：tree 
``tree >tree.txt``

## 2022.9.20

1. thread间无法进行通信。根据需求，在抢票时时间聚集度较高，因此可在执行一定次数后自动关闭进程。
2. 开发了扫描模式。通过scheldule安排定时任务，执行间隔初步定为10min，问题与1类似，时间无法通过schedule.do()进行穿透，因此也就无法结束该schedule。初步解决方法是不解决该问题，留待用户手动关闭

## 2022.10.1

新增文件proxyGet.py研究线程池的搭建，但存在免费线程耗时长、数量不稳定等问题

解决schedule无法关闭的问题。方法：
在启动的任务中新增global 全局变量，通过改变量控制schedul.run_pending的循环条件

## 2022.10.07
实际测试,发现并解决bug
ocr路径报错,起初以为绝对路径有误,后来排查发现时验证码没有请求到
发现使用`self.session.get`请求验证码时会报404，而不带任何参数使用requests.get请求时正常
猜测是cookie缺失了,对`/workbench/member/appNew/getOauthCode?userId=803873&orgId=1000&appId=760&state=2222&redirectUri=http%3A%2F%2F202.117.17.144%3A8080%2Fweb%2Findex.html?userType=1&employeeNo=2191411814&personToken=24324d82-95dc-42a5-821e-74c6ed9b1236`重定向的请求后会设置两个cookie,jessionid与sessionid,以此区分不同用户
该次请求userId与userToken必须对应
找userId找了半天,实际上这个参数在之前请求userToken时已经拿到了

## 2022.11.7
进行tobook预定时，返回message显示USERNOTLOGIN，加入loginagain模块不起效果，于是采用简单的sleep策略
预约场地都是一个时间段，因此成功预约后加入一些代码，使成功后更新场地数量并将该时段从优先级列表中删除
**项目可成功预约到场地！！**

## 2023.2.17
校方更换了验证码的验证方式，改为滑动验证。为了我的好朋友sb，特意做此版本更新。

## 2023.2.18
解决了pytz中LMT时区与CST时区不对应的bug，修复了schedule按照服务器时区执行的bug
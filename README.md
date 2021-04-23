# setu_ai for HoshinoBot

A [HoshinoBot](https://github.com/Ice-Cirno/HoshinoBot) plugin.


## 简介

基于 [HoshinoBot](https://github.com/Ice-Cirno/HoshinoBot) 的个人重度魔改版本[HoshinoBot - Kokkorobot Edition](https://github.com/LHXnois/HoshinoBot/tree/Kokkorobot)开发的涩图打分插件，当前版本基于go-cq开发。

机器人会随机发送一张涩图，用户回复这张图片打分，用户也可以自己上传图片

本插件目前的目的是为研发涩图鉴定程序收集自己的数据集

>(最终目标大概是涩图币企划的qq群实例化

TODO:
- [x] 数据收集`setu_test.py`
- [ ] 涩图自动打分`setu_marker.py`
- [ ] ...

本项目同时也有网页端 http://saki.fumiama.top/

注意：
1. 在线模式需要网页端注册密码，请在`lib.py`的`Config`类的初始化部分的`key`一项中填入密码，如果您不知道密码，请不要使用在线模式（`online`一项改为`false`）


## 功能介绍

|指令|说明|
|-----|-----|
|涩图|此插件的基础功能，叫一份涩图|
|<回复图片> 打分x|为涩图打分|
|上传图片|附带图片即可上传，如果不带图片则开启上传模式|
|网页端|获得网页端地址|
|涩批信息|获得个人一些简单的统计信息|
|<私聊bot> 开始评分|进入高效打分模式|
|<私聊bot> 结束评分|结束高效打分模式|

说明：
1. 只支持打`0`，`1`，`2`，`4`，`8`，`16`，`32`，`64`分

2. 上传模式中发送的图片都会上传，发送上传结束可以结束上传模式

3. 高效打分模式下直接回复分数，打分后立刻发送下一张图

4. 私聊模式指令简单，可以高速看图打分，群聊为防止混乱指令严格，但可以大家一起交流xp)

## 安装方式
0. 首先你要有一个配置好的[个人重度魔改版hoshino](https://github.com/LHXnois/HoshinoBot/tree/Kokkorobot)，但是本人无力撰写详细的部署说明，建议经验丰富者自行领悟

> 不要看那个readme很详细，那个是远古时期的指南，很多内容已经过时了

1. clone或者下载此仓库的代码

2. 将setu_ai文件夹放入`hoshino/modules/`文件夹中

3. 打开`hoshino/config/`文件夹中的`__bot__.py`文件，在`MODULES_ON`中加入一行`'setu_ai',`

4. 在`lib.py`的`Config`类的初始化部分的`key`一项中填入密码或者`online`一项改为`false`

5. 现在可以正常使用了~

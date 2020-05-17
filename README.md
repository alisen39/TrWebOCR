# TrWebOCR-开源的离线OCR  

## 介绍
TrWebOCR，基于开源项目 [Tr](https://github.com/myhub/tr) 构建。  
在其基础上提供了http调用的接口，便于你在其他的项目中调用。  
并且提供了易于使用的web页面，便于调试或日常使用。   

![web页面](https://images.alisen39.com/20200517184619.png)  

## 特性
* 中文识别  
快速高识别率
 
* 文字检测  
支持一定角度的旋转  

* 并发请求  
由于模型本身不支持并发，但通过tornado多进程的方式，能支持一定数量的并发请求。具体并发数取决于机器的配置。


## 安装需求  
 
### 运行平台  
* ✔ Python 3.6+  
* ✔ Ubuntu 16.04
* ✔ ️Ubuntu 18.04
* ✔ CentOS 7   
* ✔ Docker   

Windows和MacOS系统下可通过构建Docker镜像来使用，暂不支持直接部署使用  
其他Linux平台暂未测试，可自行安装测试  

### 最低配置要求  
* CPU:    1核  
* 内存:    2G  
* SWAP:   2G  

## 安装说明  
### 服务器部署
1. 安装python3.7  
    推荐使用miniconda
    
2. 执行install.py  
```
python install.py
```  

3. 安装依赖包  
``` shell script
pip install -r requirements.txt
```  

4. 运行  
``` shell script
python backend/main.py
```  

项目默认运行在8089端口，看到以下输出则代表运行成功：  
```shell script
# tr 1.5.0 https://github.com/myhub/tr
server is running: 0.0.0.0:8089
```  

### Docker部署  
1. 编译 Dockerfile  
```shell script
docker build -t TrWebOCR:latest .
```  

2. Docker run  
```shell script  
docker run -itd -p 8089:8089 --name trweb trweb-ocr:latest /bin/bash
```  
这里把容器的8089端口映射到了物理机的8089上，但如果你不喜欢映射，去掉run后面的`-p 8089:8089` 也可以使用docker的IP加`8089`来访问  

## 接口文档  
接口文档的内容放在了本项目的wiki里：
[接口文档](https://github.com/alisen39/TrWebOCR/wiki/%E6%8E%A5%E5%8F%A3%E6%96%87%E6%A1%A3)  

## 效果展示  

![文档识别](https://images.alisen39.com/20200501171943.png)  

![验证码识别](https://images.alisen39.com/20200501173211.png)

## 更新记录  

* 2020年05月17日  
    web页增加压缩功能  

* 2020年05月13日  
    解决首次使用缺少logs目录的bug  
    运行时显示的host名  
    tr-run接口增加压缩字段  

[更多记录 >>>](https://github.com/alisen39/TrWebOCR/blob/master/updateHistory.md)  


## License  
Apache 2.0

## 鸣谢
* 感谢 [myhub](https://github.com/myhub) 和它的开源项目[Tr](https://github.com/myhub/tr) 

## 最后  
项目在[GitHub](https://github.com/alisen39/TrWebOCR)和[码云](https://gitee.com/alisen39/TrWebOCR)上同步更新，国内朋友可以通过码云clone项目~  
  
如果你也喜欢这个项目，不妨给个star (^.^)✨
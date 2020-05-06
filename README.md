# TrWebOCR-开源的离线OCR  

## 介绍
TrWebOCR，基于开源项目[Tr]('https://github.com/myhub/tr')构建。  
在其基础上提供了http调用的接口，便于你在其他的项目中调用。  
并且提供了易于使用的web页面，便于调试或日常使用。 
![web页面](https://images.alisen39.com/20200501170004.png)

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
* ❌ ~~Windows~~
* ❌ ~~MacOS~~  
暂时不支持Windows和MacOS的部署，后续会提供docker部署的镜像。  
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
通过Dockerfile能够快速且简单的部署

## 效果展示  

![文档识别](https://images.alisen39.com/20200501171943.png)  

![验证码识别](https://images.alisen39.com/20200501173211.png)

## License  
Apache 2.0

## 鸣谢
* 感谢 [myhub](https://github.com/myhub) 和它的开源项目[Tr]('https://github.com/myhub/tr') 

## 最后  
如果你也喜欢这个项目，不妨给个star (^.^)✨
> ### Linux-op-manager主要是用于集中管理维护Linux服务器，主要功能有：远程执行命令、文件下发、自动部署环境等，其他功能待开发！
### 环境如下：
```
centos6.5
python2.7.11
salt-master-2015.5.10-2
salt-api-2015.5.10-2
MySQL-python (1.2.5)
pip (8.1.2)
setuptools (26.1.1)
singledispatch (3.4.0.3)
six (1.10.0)
tornado (4.4.1)
torndb (0.3)
bootstrap3
```
### 架构介绍
#### 架构图
Salt-api（用于Salt客户端与服务端沟通的媒介）
      |
Python（编程语言，需要选择Web框架）
      |
Tornado（比较简单容易实现的Web框架）
      |
Bootstrap3（用于前端界面设计）

#### 效果图
![image](https://github.com/minminmsn/linux-op-manager/blob/master/static/linux-op-manager.jpg)

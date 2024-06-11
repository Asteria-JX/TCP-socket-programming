# TCP 套接字编程项目

本项目是基于TCP的客户端-服务器模型，支持数据包的发送、接收和数据反转。该项目铜鼓Python语言使用TCP套接字进行网络通信，并通过通信来反转给定文本文件的段落。通过多线程在服务器端的实现，允许同时处理多个客户端请求。

## 目录

- [概述](#概述)
- [特点](#特点)
- [功能](#功能)
- [快速开始](#快速开始)
  - [先决条件](#先决条件)
  - [安装](#安装)
- [使用方法](#使用方法)
  - [服务器](#服务器)
  - [客户端](#客户端)
- [报文格式](#报文格式)

## 概述

该项目由两个主要部分组成：TCP服务器和TCP客户端。服务器监听连接并反转客户端发送的文本段落。客户端读取文本文件，向服务器发送段落，接收反转后的段落，并将它们保存到输出文件中。

## 特点

- 使用 `ThreadPoolExecutor` 实现多线程服务器处理。
- 使用 `select` 模块实现非阻塞服务器操作。
- 为初始化、同意、反转请求和反转回答定义了自定义消息类型。
- 为每个反转请求随机化段落长度，在指定范围内。

## 功能

### 客户端功能

- 读取文件中的内容，并根据指定的最小和最大长度随机分割文件，逐次发送至服务器。
- 接收服务器反转后的数据并保存至输出文件。

#### 服务器功能

- 监听并接受来自客户端的连接。
- 接收客户端发送的数据包并根据数据类型处理。
- 将接收到的数据反转后发送回客户端。
- 使用多线程技术，支持多客户端同时连接。

## 快速开始

### 先决条件

- Python 3.x
- Git

### 安装

1.克隆仓库：

```sh
git clone https://github.com/Asteria-JX/TCP-socket-programming.git
```

2.进入项目目录：

```
cd TCP-socket-programming
```

3.安装所需的包

## 使用方法

### 服务器

启动服务器，请运行：

```
python tcpserver.py
```

服务器将在4216端口上开始监听。

### 客户端

运行客户端，请执行以下命令并附上相应的参数：

```
python tcpclient.py <服务器IP> <服务器端口> <文件路径> <Lmin> <Lmax>
```

客户端将连接到服务器，发送指定文件的段落，接收反转后的段落，并将其保存到reversed_content.txt。
## 报文格式

Client -> Server	    Initialization 报文，Type=1 

```bash
|  	Type   | 		N	 	    |      
|   2 Bytes  | 	4 Bytes  	|
```

Server -> Client	    agree 报文，Type=2

```
|  	Type   | 	  
| 2 Bytes  | 	
```

Client -> Server	    reverseRequest 报文，Type=3

```
|  	Type   | 		N	     	|        	Data			  	|
| 2 Bytes  | 	4 Bytes  	|
```

Server -> Client	    reverseAnswer 报文，Type=4

```
|  	Type   | 		N	 	    |      reverseData			|
| 2 Bytes  | 	4 Bytes  	|
```




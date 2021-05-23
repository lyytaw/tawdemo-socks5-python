# tawdemo-socks5-python

一个Python语言编写的sock5代理工具DEMO，比较简单，仅具有学习价值，不具备生产特性，请勿用于生产。之前用c语言写过一版，不是很熟c语言，写完初版后就写不下去了，所以这次又写了一版python的，基于asyncio。

### 运行环境

类unix系统、python3.6+

无需安装第三方库

### 使用方式

**安装**

```bash
git clone https://github.com/lyytaw/tawdemo-socks5-python.git
cd tawdemo-socks5-python
python setup.py build 
python setup.py install
```

**服务器**

```bash
nohup tawsocks-server -p [本地监听端口] -P [密码] &
```

**客户端**

密码必须与服务器密码一致

```bash
nohup tawsocks-client -lp [本地监听端口] -rp [服务器端口] -rh [服务器地址] -P [密码] &
```

### 版本特性

v1.2 更换项目名为tawdemo-socks5-python

v1.1 支持UDP协议

v1.0 仅支持TCP协议的代理

### 协议

本项目使用[MIT协议](https://github.com/lyytaw/tawdemo-socks5-python/blob/master/LICENSE)

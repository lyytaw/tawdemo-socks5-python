# skyun

仅可用于正常学术研究以及技术搜索需要

### 运行环境

类unix系统、python3.6+

无需安装第三方库

### 使用方式

**安装**

```bash
pip install skyun
```

**服务器**

```bash
nohup skyserver -p [本地监听端口] -P [密码] &
```

**客户端**

密码必须与服务器密码一致

```bash
nohup skyclient -lp [本地监听端口] -rp [服务器端口] -rh [服务器地址] -P [密码] &
```

### 版本特性

v1.1 支持UDP协议

v1.0 仅支持TCP协议的代理

### 协议

本项目使用[MIT协议](https://github.com/thingerpig/tepig-bridge-python/blob/master/LICENSE)

# pyfan

饭否客户端python版。

## 安装

下载全部代码，运行：

    pip install -r requirements.txt


## 配置

创建一个config.json的文件，加入申请的客户端ID：

    {
        "CLIENT_KEY": "XXXX",
        "CLIENT_SECRET": "xxxx"
    }

## 初始化

用户登录方式，运行登录用webserver：

    python weblogin.py

浏览器打开： http://localhost:8880/ 将自动转向饭否授权页面，授权后返回显示登录用户名。登录成功以后相关的授权码会被保存在config.json中，之后即可退出webserver，开始使用本客户端。

## 使用

    python
    >> import pyfan
    >> pyfan.timeline(count, page)
    >> pyfan.mentions(count, page)
    >> pyfan.usertimeline(user_id, count, page)
    >> pyfan.showstatus(status_id)
    >> pyfan.destroy(status_id)
    >> pyfan.post(status, photo)

* count为条数，默认为10，最大不超过60
* page为页号，默认为0
* user_id为用户ID，显示在用户名后面的括号中
* status_id为消息ID，显示在时间后面的括号中
* status为消息内容
* photo为图片文件名，默认为空

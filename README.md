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
    >> pyfan.showstatus(status_id or index)
    >> pyfan.destroy(status_id or index)
    >> pyfan.post(status[, photo])
    >> pyfan.repost(status, index)
    >> pyfan.reply(status, index)
    >> pyfan.replyall(status, index)
    >> pyfan.showcontext(index)

* status_id和index通过类型自动判断
* count为条数，默认为8，最大不超过60
* page为页号，默认为0
* user_id为用户ID，显示在用户名后面的括号中，字符串类型
* status_id为消息ID，显示在时间后面的括号中，字符串类型
* status为消息内容
* photo为图片文件名，默认为空
* index为消息编号，显示在最前在的方括号中，整数类型，注意：只能引用最近一次timeline/mentions/usertimelin/showstatus/showcontext调用结果。

## 命令行使用

（感谢令狐增加此功能）

    python cli.py help            # 获得使用帮助
    python cli.py                 # 获得timeline最新8条(默认值)信息
    python cli.py mention 30      # 显示最新30条“提到我的”消息
    python cli.py timeline 30 2   # 按每页30条计算，显示第二页timeline消息
    python cli.py timeline page=2 # 按每页8条(默认值)计算，显示第二页timeline消息
    python cli.py this is a demo  # 发送内容为“this is a demo”的消息
    python cli.py "text=this is a demo" "photo=../photo/test.png"  
            # 发送内容为“this is a demo”的消息，并附带指定图片。注意图片后缀必需为png或jpg或gif。

#coding:utf-8
import sys
import os
import myhandler

COMMAND = {
    'timeline':(u'显示timeline的消息。', 
                [('count', False, u'显示的条数。默认为10，如果此数大于60，则会强制指定为60'),
                 ('page', False, u'页号。默认为0')],
                myhandler.handle_timeline),
    
    'mention':(u'显示提到我的消息。',
                [('count', False, u'显示的条数。默认为10，如果此数大于60，则会强制指定为60'),
                 ('page', False, u'页号。默认为0')],
                myhandler.handle_mention),

    'user':(u'显示指定用户的timeline消息。',
                [('user_id', True, u'用户ID'),
                 ('count', False, u'显示的条数。默认为10，如果此数大于60，则会强制指定为60'),
                 ('page', False, u'页号。默认为0')],
                myhandler.handle_usertimeline),

    'post':(u'显示指定用户的timeline消息。注意，消息和图片不可同时为空',
                [('text', False, u'消息内容'),
                 ('photo', False, u'图片路径')],
                myhandler.handle_post),

    'help':(u'显示本帮助信息',
            [],
            myhandler.handle_help)
}

#疑似命令, 加入疑似命令是为了防止用户原本希望执行命令但因为写错了而将信息直接发送出去
LIKE_COMMAND = ['mentions', 'timelines', 'users', 'usertimeline', 'usertimelines', 'send', 'put']


def get_command(argv):
    global COMMAND

    if len(argv) == 0:
        return 'timeline', ''
    elif argv[0] in COMMAND.keys() or argv[0] in LIKE_COMMAND:
        return argv[0], argv[1:]
    else:
        return 'post', argv

def get_handler(command):
    global COMMAND

    if command not in COMMAND.keys():
        print(u"未知命令: %s. 请输入 %s help 查看帮助信息" % (command, os.path.basename(sys.argv[0])))
        return None
    else:
        return COMMAND[command][2]

if __name__ == "__main__":
    argv = sys.argv[1:]
    command, remain = get_command(argv)

    handler = get_handler(command)
    if handler != None:
        handler(COMMAND, command, remain)
    else:
        print("找不到%s对应的命令处理函数" % command)

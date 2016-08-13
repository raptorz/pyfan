#coding:utf-8
import sys
import os
import glob

#import pyfan_mock as pyfan
import pyfan

def _parse_argv(commands, cmd, argv):
    #首先尝试按字典解析
    arg_dict = {}
    dict_mode = False
    for arg in argv:
        if '=' in arg:
            k,v = arg.split('=')
            arg_dict[k] = v
            dict_mode = True
        elif dict_mode:
            raise BaseException("不能混用顺序模式和字典模式")

    arg_conf_list = commands[cmd][1]
    
    #如果不是字典模式，则按顺序创造一个字典
    if not dict_mode:
        for index, (arg_name, must_be, arg_desc) in enumerate(arg_conf_list):
            if index < len(argv):
                arg_dict[arg_name] = argv[index]

    #检查必需的参数是否存在
    for arg_name, must_be, arg_desc in arg_conf_list:
        if must_be and not arg_dict.has_key(arg_name):
            raise BaseException("必需的字段 %s 不存在" % arg_name)

    return arg_dict
    

def handle_timeline(commands, cmd, argv):
    arg_dict = _parse_argv(commands, cmd, argv)
    if 'count' not in arg_dict:
        arg_dict['count'] = 10
    if 'page' not in arg_dict:
        arg_dict['page'] = 0
    count = int(arg_dict['count'])
    page = int(arg_dict['page'])

    pyfan.timeline(count, page)



def handle_mention(commands, cmd, argv):
    arg_dict = _parse_argv(commands, cmd, argv)
    if 'count' not in arg_dict:
        arg_dict['count'] = 10
    if 'page' not in arg_dict:
        arg_dict['page'] = 0
    count = int(arg_dict['count'])
    page = int(arg_dict['page'])

    pyfan.mention(count, page)

def handle_usertimeline(commands, cmd, argv):
    arg_dict = _parse_argv(commands, cmd, argv)
    if 'count' not in arg_dict:
        arg_dict['count'] = 10
    if 'page' not in arg_dict:
        arg_dict['page'] = 0
    user_id = arg_dict['user_id']
    count = int(arg_dict['count'])
    page = int(arg_dict['page'])

    pyfan.mention(user_id, count, page)

def handle_post(commands, cmd, argv):
    arg_dict = {}
    if len(argv) == 0:
        raise "不能发送空消息"
    if len(argv) > 2:
        arg_dict['text'] = ' '.join(argv)
    else:
        arg_dict = _parse_argv(commands, cmd, argv)

    if 'text' not in arg_dict:
        arg_dict['text'] = u"发送图片"
    if 'photo' not in arg_dict:
        arg_dict['photo'] = ''

    text = arg_dict['text']
    photo = arg_dict['photo']
    if photo != '' and not os.path.exists(os.path.expanduser(photo)):
        raise BaseException("图片 %s 不存在" % photo)

    pyfan.post(text, photo)
    

def handle_help(commands, cmd, argv):
    print('支持的命令: ')
    for command, desc in commands.items():
        print("\n    %s: %s" % (command, desc[0]))
        print("    本命令支持 %d 个参数" % len(desc[1]))
        if len(desc[1]) > 0:
            print("    参数详述：")
        for arg_name, must_be, arg_desc in desc[1]:
            print("        %s%s: %s" % (arg_name, "(必需)" if must_be else "", arg_desc))

    print('\n注意：如果完全不带参数，则以默认数量显示timeline。如果参数中不包含有效命令，则默认为发送消息。')
    print('\n参数有两种写法：一种是顺序写法，只需要写值即可。顺序必须保持与说明中一致。')
    print('另一种是 key=value 的写法，key的名字就是帮助中提到的名字。等号前后不能有空格。如果value包含空格，请写成带双引号的形式："key=value with space"，这种写法顺序不重要，而且可以省略非必需的参数。但要必需的参数必须存在，否则会报错')
    print('\n顺序写法和key=value写法不可混用')
    print('\n注意：如果要发送句首为命令的内容。可以在前面明确指定post命令，或将内容用引号（"）括起来')
    print('\n用法示例：')
    print('     python %s mention 30 //显示最新30条“提到我的”消息' % os.path.basename(sys.argv[0]))
    print('     python %s timeline 30 2 //按每页30条计算，显示第二页timeline消息' % os.path.basename(sys.argv[0]))
    print('     python %s timeline page=2 //按每页10条(默认值)计算，显示第二页timeline消息' % os.path.basename(sys.argv[0]))
    print('     python %s this is a demo //发送内容为“this is a demo”的消息' % os.path.basename(sys.argv[0]))
    print('     python %s "text=this is a demo" photo=../photo/test.png //发送内容为“this is a demo”的消息，并附带指定图片。注意图片后缀必需为png或jpg或gif' % os.path.basename(sys.argv[0]))

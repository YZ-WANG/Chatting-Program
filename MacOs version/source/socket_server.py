import socket
import threading
import time
import logging
import sys
import os
import struct

# 调整python编码形式，有ASCII转为utf-8
defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)

logging.basicConfig(level=logging.INFO)

# 服务器端存储用户数据，初始化为空
# signed_list=[] # (name,password)构成已注册可登陆用户
signed_list=[('wyz','hzs')]
user_list=[]  # name构成在线用户名列表
sock_list=[]  # (sock,name)构成的socket与用户名映射表格

# 返回当前在线用户列表
def show_user_list(sock):
    online_usr = '【系统消息】\n----在线用户列表----\n'
    for i in user_list:
        online_usr = online_usr +'    ' +i+'\n'
    sock.sendall(online_usr.encode('utf-8'))

# 向其他所有用户广播消息
def broadcast_msg(message, current_name):
    for (sock,name) in sock_list:
        if (name != current_name):
            sock.sendall(message.encode('utf-8')) # 对消息编码

# 返回用户名对应的socket
def get_sock(name):
    for i in sock_list:
        if (name==i[1]):
            return i[0]

# 向指定用户名的用户发送消息
def send_msg_to(receiver_name, msg):
    sock = get_sock(receiver_name) #根据用户名找到socket
    sock.sendall(msg.encode('utf-8'))

# 登陆验证，更新在线用户名和socket
def ifcan_log_in(name_pwd,sock):
    # 从name_pwd分离出name和pwd
    name = name_pwd.split()[0]
    pwd = name_pwd.split()[1]
    if (name,pwd) in signed_list: # 用户名已被注册，可使用
        sign_in_msg = '【系统消息】 用户名为 %s 的用户上线...' % name # 成功上线
        broadcast_msg(sign_in_msg, name)  # 广播新用户上线
        user_list.append(name) # 更新用户名列表
        sock_list.append((sock,name)) # 更新映射表
        sock.send(b'1')
        # 向其他用户反馈在线用户列表
        for i in user_list:
            if i!=name:
                dst_sock = get_sock(i)
                show_user_list(dst_sock)
        time.sleep(1) # 延时
        return True
    else:
        sock.send(b'0')
        sock.close()
        return False

# 信息接收循环--总控部分
def receive_loop(sock,name):
    if_loop = True
    while (if_loop):
        if_exe = False
        cmd = sock.recv(1024).decode('utf-8')  # 收到Message
        # 接收到客户端退出请求
        if cmd == '-exit':
            if_exe = True
            if_loop = False
        # 接收到客户端获取在线用户列表请求
        if cmd == '-user_list':
            if_exe = True
            show_user_list(sock)
        # 接收到客户端私聊请求
        if cmd =='-p2p':
            if_exe = True
            sys_msg ='【系统消息】\n----进入私聊模式，输入私信用户名----\n----用户列表获取中...----\n'
            sock.sendall(sys_msg.encode('utf-8'))
            show_user_list(sock)
            receiver = sock.recv(1024).decode('utf-8')
            if receiver in user_list:
                if_loop = p2p_msg(sock,name,receiver)
            sys_msg ='【系统消息】\n----退出私聊模式，返回主页----'
            sock.send(sys_msg.encode('utf-8'))
        # 接收到客户端群聊请求
        if cmd == '-public':
            if_exe = True
            sys_msg ='【系统消息】\n----进入群聊模式，发言公开----'
            sock.send(sys_msg.encode('utf-8'))
            if_loop = message_public(sock,name)
            sys_msg ='【系统消息】\n----退出群聊模式，返回主页----'
            sock.send(sys_msg.encode('utf-8'))
        if not if_exe:
            sys_msg= '【系统消息】！！！该操作不可执行！！！'
            sock.sendall(sys_msg.encode('utf-8'))

# 群聊发言
def message_public(sock,name):
    while True:
        cmd_or_msg = sock.recv(1024).decode('utf-8')
        if cmd_or_msg=='-quit':
            return True
        msg = '【群聊模式】%s: ' % name + cmd_or_msg
        broadcast_msg(msg, name)

# 私聊消息发送
def p2p_msg(sock,name,receiver):
    while True:
        cmd_or_msg = sock.recv(1024).decode('utf-8')
        if cmd_or_msg == '-quit':  # 收到退出命令
            return True
        if cmd_or_msg == '-file_trans': 
            #deal_file(sock,name,receiver);
            msg = '【私信】%s:向你分享了文件%s\n【本地】文件已成功接收' % (name,deal_file(sock,name,receiver))
        else: msg = '【私信】%s: '%name + cmd_or_msg
        send_msg_to(receiver,msg)

def deal_file(sock,name,receiver):
    rec_sock = get_sock(receiver)
    rec_sock.sendall('-file_trans'.encode('utf-8'))
    logging.info('start file_trans...')
    sock.settimeout(600)
    fileinfo_size = struct.calcsize('128sl')
    buf = sock.recv(fileinfo_size)
    rec_sock.sendall(buf)
    if buf:
        filename,filesize = struct.unpack('128sl', buf)
        recvd_size = 0  # 定义已接收文件的大小

        while not recvd_size == filesize:
            if filesize - recvd_size > 1024:
                data = sock.recv(1024)
                recvd_size += len(data)
            else:
                data = sock.recv(filesize - recvd_size)
                recvd_size = filesize
            rec_sock.sendall(data)
        logging.info('end file_trans...')
        return filename.decode('utf-8').strip('\00')

# 用户下线
def leaving(sock,name):
    msg='【系统消息】啊朋友再见，啊朋友再见，啊朋友再见吧再见吧再见吧～\n'
    sock.sendall(msg.encode('utf-8'))  # 用户离开，服务器发送关闭用户端接收关闭语句
    leaving_msg = '【系统消息】用户名为 %s 的用户离开了聊天系统' % name
    broadcast_msg(leaving_msg, name)  # 广播用户的离开
    sock.close()
    user_list.remove(name)
    sock_list.remove((sock, name))
    for i in user_list:
        dst_sock=get_sock(i)
        show_user_list(dst_sock)

# 用户线程--总控
def tcp_link(sock, addr):
    # 注册用户或用户登陆
    while True:
        msg = sock.recv(1024).decode('utf-8') # 获取请求
        logging.info('msg is %s' % msg)
        # 响应注册用户的请求
        if msg == '-sign_up':
            name_pwd = sock.recv(1024).decode('utf-8')
            name = name_pwd.split()[0]
            pwd = name_pwd.split()[1]
            logging.info('sign_up,pwd is %s' % pwd)
            if_signed=False
            for i in signed_list:
                if name==i[0]:
                    if_signed=True
                    break
            # if ((name,pwd) in signed_list):
            if if_signed:
                logging.info('name has been used')
                sock.send(b'0')
            else:
                signed_list.append((name,pwd))
                sock.send(b'1')
                logging.info('successfully sign up')
        # 响应用户登陆的请求
        elif msg == '-log_in':
            name_pwd = sock.recv(1024).decode('utf-8')
            name = name_pwd.split()[0]
            if ifcan_log_in(name_pwd,sock): #登陆成功，开启总控
                logging.info('Accept new connection from %s:%s...' % addr)
                show_user_list(sock)     # 返回所有当前在线的用户
                receive_loop(sock,name)  # 持续接收message进行响应--总控
                leaving(sock,name)       # 退出程序
            logging.info('Connection from %s:%s closed.' % addr)
            break
        else:
            logging.info('Connection from %s:%s closed.' % addr)
            break

if __name__=='__main__':
    # 选择ipv4协议族和流动式套接层
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.bind(('127.0.0.1',8000))
    s.listen(5)   #最多允许的用户在线数量
    logging.info('Waiting for connection...')
    while True:
        sock,addr=s.accept()
        t=threading.Thread(target=tcp_link,args=(sock,addr))
        t.start()

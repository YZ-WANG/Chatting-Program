from tkinter import *
import tkinter as tk
from tkinter import messagebox  # 用于注册时的messagebox error
import time
import socket
import logging
import threading
import os
import struct
import sys

# 调整python编码形式，有ASCII转为utf-8
defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)

logging.basicConfig(level=logging.INFO)

# 从Frame类派生出App类进行功能布局
class ChatApp(Frame):
    # 初始化用户socket以及界面
    def __init__(self, master=None):
        Frame.__init__(self, master) # 调用父类Frame初始化
        logging.info('socket is building')
        # 构建当前用户的socket
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 连接到server
        self.s.connect(('127.0.0.1', 8000))
        logging.info('Socket has been built')
        self.pack() # grid布局
        self.createWidgets()
        # 系统操作提醒
        self.msg_list.insert(END,'【系统消息】请在左侧界面登陆或注册新用户... \n')
        logging.info('__init__END')

    # 使用grid布置界面控件
    def createWidgets(self):
        # 导入图片
        abs_path = os.path.abspath(__file__) # 返回当前所属文件夹的绝对路径
        path = abs_path.split('/')
        path[len(path)-1] = 'pic.png'
        pic_path=''
        for i in range(len(path)-1):
            pic_path = pic_path + '/' +path[i+1]
        self.photo = PhotoImage(file=pic_path)
        self.imgLabel = Label(self,image=self.photo)#把图片整合到标签类中
        self.imgLabel.grid(row=1,column=0)
        # 用户名、密码输入
        self.name_lable = Label(self, text='用户名')
        self.name_lable.grid(row=4,column=0,sticky=W)
        self.pwd_label = Label(self, text='密码')
        self.pwd_label.grid(row=5,column=0,sticky=W)
        self.var_usr_name = tk.StringVar()
        # self.var_usr_name.set('example@python.com')
        self.entry_usr_name = Entry(self, textvariable=self.var_usr_name)
        self.entry_usr_name.grid(row=4, column=0)
        self.var_usr_pwd = tk.StringVar()
        self.entry_usr_pwd = Entry(self, textvariable=self.var_usr_pwd, show='*')
        self.entry_usr_pwd.grid(row=5, column=0)
        # 登陆、注册按钮
        self.log_in_Button = Button(self, text=' 用户登陆 ', command=self.user_log_in,state='normal')
        self.log_in_Button.grid(row=6,column=0)
        self.sign_up_Button = Button(self, text=' 注册用户 ', command=self.usr_sign_up,state='normal')
        self.sign_up_Button.grid(row=7,column=0)
        # 聊天交互界面
        self.msg_list=Text(self,bg='Ivory')
        self.msg_list.grid(row=0,column=5,rowspan=10,columnspan=2)
        # 信息输入界面
        self.msg_input = Entry(self)
        self.msg_input.grid(row=10,column=1,columnspan=5)
        # 按钮创建与布置
        self.send_Button = Button(self, text='发送消息', command=self.submit,state='disable')
        self.send_Button.grid(row=10,column=6,sticky=W)
        self.file_Button = Button(self, text='发送文件', command=self.submit_file,state='disable')
        self.file_Button.grid(row=10,column=6)
        self.user_Button = Button(self, text='在线列表', command=self.user_list,state='disable')
        self.user_Button.grid(row=2,column=7)
        self.p2p_Button = Button(self, text='私聊模式', command=self.p2p,state='disable')
        self.p2p_Button.grid(row=3,column=7)
        self.pub_Button = Button(self, text='群聊模式', command=self.public,state='disable')
        self.pub_Button.grid(row=4,column=7)
        self.back_Button = Button(self, text='返回主页', command=self.back,state='disable')
        self.back_Button.grid(row=5,column=7)
        self.exit_Button = Button(self, text='退出系统', command=self.exit,state='disable')
        self.exit_Button.grid(row=6,column=7)

    # 按钮动作设置
    def exit(self):
        msgcontent='-exit'
        self.s.sendall(msgcontent.encode('utf-8'))
        self.p2p_Button.config(state='disable')
        self.pub_Button.config(state='disable')
        self.user_Button.config(state='disable')
        self.exit_Button.config(state='disable')
        self.back_Button.config(state='disable')

    def p2p(self):
        self.send_Button.config(state='normal')
        self.file_Button.config(state='normal')
        self.p2p_Button.config(state='disable')
        self.pub_Button.config(state='disable')
        msgcontent = '-p2p'
        self.s.sendall(msgcontent.encode('utf-8'))
        self.back_Button.config(state='normal')
        self.user_Button.config(state='disable')
        self.exit_Button.config(state='disable')

    def user_list(self):
        msgcontent = '-user_list'
        self.s.sendall(msgcontent.encode('utf-8'))

    def public(self):
        self.send_Button.config(state='normal')
        self.p2p_Button.config(state='disable')
        self.pub_Button.config(state='disable')
        self.user_Button.config(state='disable')
        msgcontent = '-public'
        self.s.sendall(msgcontent.encode('utf-8'))
        self.back_Button.config(state='normal')
        self.exit_Button.config(state='disable')

    def back(self):
        msgcontent = '-quit'
        self.s.sendall(msgcontent.encode('utf-8'))
        self.send_Button.config(state='disable')
        self.p2p_Button.config(state='normal')
        self.pub_Button.config(state='normal')
        self.user_Button.config(state='normal')
        self.exit_Button.config(state='normal')
        self.back_Button.config(state='disable')

    def submit(self):
        msgcontent = self.msg_input.get() or ' '
        if msgcontent:
            logging.info('[submit]:%s'%msgcontent)
            self.msg_input.delete(0,END)
            self.msg_list.insert(END,time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())+'\n')
            self.s.sendall(msgcontent.encode('utf-8'))
            self.msg_list.insert(END,'【本地】'+msgcontent+'\n')
            self.msg_list.see(END)
            if msgcontent=='-exit':
                self.s.close()
                logging.info('[system]SOCK END')

    def submit_file(self):
        msgcontent = '-file_trans'
        self.s.sendall(msgcontent.encode('utf-8'))
        # time.sleep(1)
        file_path = self.msg_input.get()
        if file_path:
            logging.info('[submit_file]:%s' % file_path)
            self.msg_input.delete(0,END)
            self.msg_list.insert(END,time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())+'\n')

            if os.path.isfile(file_path):
                # 定义定义文件信息。128s表示文件名为128bytes长，l表示一个int或log文件类型，在此为文件大小
                fileinfo_size = struct.calcsize('128sl')
                # 定义文件头信息，包含文件名和文件大小
                fhead = struct.pack('128sl', os.path.basename(file_path).encode('utf-8'),
                                    os.stat(file_path).st_size)
                self.s.sendall(fhead)

                fp = open(file_path, 'rb')
                while True:
                    data = fp.read(1024)
                    if not data:
                        break
                    self.s.sendall(data)
                logging.info('[system]successfully send file')

            filename = file_path.split('/')[len(file_path.split('/'))-1]
            self.msg_list.insert(END,'【本地】文件%s已传输完成\n' % filename )
            self.msg_list.see(END)
            if msgcontent=='-exit':
                self.s.close()
                logging.info('[system]SOCK END')

    # 用户登陆
    def user_log_in(self):
        logging.info('[user_log_in]')
        msgcontent = '-log_in'
        self.s.sendall(msgcontent.encode('utf-8'))
        name = self.entry_usr_name.get()
        pwd = self.entry_usr_pwd.get()
        name_pwd = name+' '+pwd
        logging.info('name_pwd=%s' %name_pwd)
        time.sleep(1)
        self.s.sendall(name_pwd.encode('utf-8'))
        re = int(self.s.recv(1024).decode('utf-8'))
        logging.info('re=%s'%re)
        if not re:
            self.msg_list.insert(END,"【系统消息】用户名或密码错误，请重新登录\n")
        else:
            self.msg_list.insert(END, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '\n')
            self.msg_list.insert(END,"【系统消息】Welcome %s \n" %name)
            self.main_loop()
            logging.info('[user_log_in]end')
            self.log_in_Button.config(state='disable')
            self.sign_up_Button.config(state='disable')
            self.p2p_Button.config(state='normal')
            self.pub_Button.config(state='normal')
            self.user_Button.config(state='normal')
            self.exit_Button.config(state='normal')
            self.entry_usr_name.config(state='disable')
            self.entry_usr_pwd.config(state='disable')

    # 用户注册窗口
    def usr_sign_up(self):
        # 设计用户注册动作
        def sign_to_chat(s):
            np = new_pwd.get()
            logging.info('np=%s' % np)
            npf = new_pwd_confirm.get()
            logging.info('npf=%s' % npf)
            nn = new_name.get()
            if np != npf:
                logging.info('[user_sign_Error]passwords not same')
                tk.messagebox.showerror('Error', '前后两次密码必须一致!')
            else:
                logging.info('[user_sign_up]')
                msgcontent = '-sign_up'
                s.sendall(msgcontent.encode('utf-8'))
                new_name_pwd = nn+' '+np
                time.sleep(1)
                s.sendall(new_name_pwd.encode('utf-8'))
                re = int(s.recv(1024).decode('utf-8'))
                if not re:
                    tk.messagebox.showerror('Error', '该用户名已被注册！')
                else:
                    tk.messagebox.showinfo('Welcome', '新用户注册成功！')
                    window_sign_up.destroy()
        # 设计用户注册弹窗界面
        window_sign_up = tk.Toplevel(self)
        window_sign_up.geometry('350x200')
        window_sign_up.title('注册界面')

        new_name = tk.StringVar()
        new_name.set('example')
        tk.Label(window_sign_up, text='用户名: ').place(x=10, y= 10)
        entry_new_name = tk.Entry(window_sign_up, textvariable=new_name)
        entry_new_name.place(x=150, y=10)

        new_pwd = tk.StringVar()
        tk.Label(window_sign_up, text='密码: ').place(x=10, y=50)
        entry_usr_pwd = tk.Entry(window_sign_up, textvariable=new_pwd, show='*')
        entry_usr_pwd.place(x=150, y=50)

        new_pwd_confirm = tk.StringVar()
        tk.Label(window_sign_up, text='确认密码: ').place(x=10, y= 90)
        entry_usr_pwd_confirm = tk.Entry(window_sign_up, textvariable=new_pwd_confirm, show='*')
        entry_usr_pwd_confirm.place(x=150, y=90)
        logging.info('[user_ooooo]')
        btn_comfirm_sign_up = Button(window_sign_up, text='确认注册', command=lambda:sign_to_chat(self.s))
        btn_comfirm_sign_up.place(x=150, y=130)

    def send_msg(self):
        logging.info('[send_msg]begin')
        while True:
            my_word =self.msg_input.get()
            self.s.sendall(my_word.encode('utf-8'))
            if my_word == ('-exit'):
                break
        logging.info('[send_msg]end')

    # 用户端功能总控(接收服务器端功能指令)
    def get_msg(self):
        ##########################################
        # 设计文件接收函数
        def deal_file(s):
            logging.info('start receive...')
            s.settimeout(600)
            fileinfo_size = struct.calcsize('128sl')
            buf = s.recv(fileinfo_size)
            if buf:
                filename,filesize = struct.unpack('128sl', buf) # 获取文件名与大小
                fn = filename.decode('utf-8').strip('\00') # 获取字符串形式文件名（包括后缀）
                new_filename = os.path.join('./receive/', ('new_' + fn)) # 设置文件接收存储地址

                recvd_size = 0  # 定义已接收文件的大小
                fp = open(new_filename, 'wb')

                while not recvd_size == filesize:
                    if filesize - recvd_size > 1024:
                        data = s.recv(1024)
                        recvd_size += len(data)
                    else:
                        data = s.recv(filesize - recvd_size)
                        recvd_size = filesize
                    fp.write(data)
                fp.close()
                #filename = file_path.split('/')[len(file_path.split('/'))-1]
                #self.msg_list.insert(END,'【本地】文件%s已传输完成\n' % filename )
                logging.info('end receive %s...' % fn)
        ##########################################
        logging.info('[get_msg]begin')
        while True:
            data = self.s.recv(1024).decode('utf-8')
            if data == '-file_trans': deal_file(self.s)
            elif data:
                self.msg_list.insert(END, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '\n')
                self.msg_list.insert(END, data+'\n')
                self.msg_list.see(END)
                if data == "【系统消息】啊朋友再见，啊朋友再见，啊朋友再见吧再见吧再见吧～\n":
                    self.s.close()
                    logging.info('[system]SOCK END')
                    break
            else: break
        logging.info('[get_msg]end')
        # self.destroy()

    # 用户线程创建--总控
    def main_loop(self):
        logging.info('[main_loop]begin')
        self.get_loop=threading.Thread(target=self.get_msg)
        self.get_loop.start()
        logging.info('[main_loop]end')


if __name__=='__main__':
    # 实例化客户端
    app = ChatApp()
    # 设置窗口标题:
    app.master.title('聊天系统')
    # 进入客户端总控程序
    app.mainloop()

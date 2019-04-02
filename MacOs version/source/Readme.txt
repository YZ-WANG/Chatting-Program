运行环境：VmWare Fusion 10.1.3下 ubuntu 16.04.4
编译工具：python 3.6.5，PyInstaller 3.4
源文件：socket_server.py，socket_user.py 和 美化界面的图片pic.png
说明：直接终端运行指令 $ python3 socket_server.py 和 $ python3 socket_user.py，也可以运行聊天系统。但由于PyInstaller打包之后，在mac上tk只能识别gif图片，因此bin文件里的可执行文件打开的客户端稍有不同。另外如果有传输文件需要，需要建立目录“./receive”文件夹，接收的文件会存储在该文件夹目录中。

# cmdb



## 安装python3
环境Python 3.8.9
```
yum install zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gcc make libffi-devel -y
wget http://npm.taobao.org/mirrors/python/3.8.9/Python-3.8.9.tgz

mv Python-3.8.9.tgz /usr/local/
./configure prefix=/usr/local/python3

make && make install
/usr/local/python3/bin/python3
/usr/local/python3/bin/pip3 install -r requirements.txt
```

##启动命令
```
bash start.sh
bash stop.sh
```

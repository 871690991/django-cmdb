# cmdb
```
cmdb1.0版本实现、应用、业务线、物理机、虚拟机管理功能、openstack管理
```


## python环境
环境Python 3.8.9
```shell
yum install zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gcc make libffi-devel -y
wget http://npm.taobao.org/mirrors/python/3.8.9/Python-3.8.9.tgz

mv Python-3.8.9.tgz /usr/local/
./configure prefix=/usr/local/python3

make && make install
/usr/local/python3/bin/python3
/usr/local/python3/bin/pip3 install -r requirements.txt


```

##启动命令
```shell
创建管理员
python manage.py createsuperuser
初始化数据库
python manage.py migrate 
python manage.py makemigrations
#本地debug运行python manage.py runserver 8080
服务器运行
bash start.sh
bash stop.sh
```

#注意事项
首次登录需要在django admin后台、创建admin组、把admin用户添加到admin组才有权限访问
![image](/static/img/demo/6.png)
![image](/static/img/demo/7.png)

#前端效果
![image](/static/img/demo/1.png)
![image](/static/img/demo/2.png)
![image](/static/img/demo/3.png)
![image](/static/img/demo/4.png)
![image](/static/img/demo/5.png)
## 如何打包镜像
###1.登录任意一台linux服务器，进入项目的根目录
```commandline
docker build -t execution-engine .
docker tag imageID artifactory.test.com:8081/sse/mid/execution-engine:0.1.1
docker login artifactory.test.com:8081
docker push artifactory.test.com:8081/sse/mid/execution-engine:0.1.1
```
##如何启动镜像
###1.启动镜像时，需要添加两个环境变量DATA_ID和SERVER_ADDRESS，分别是nacos服务器上将要注册的服务名和nacos的服务器地址，譬如：
```commandline
SERVER_ADDRESS:http:10.112.15.114:8848
DATA_ID:execution-engine
```

##windows下启动服务
1、运行根目录的main.py方法
2、运行celery命令
```commandline
celery -A celery_app worker -l info -P eventlet
celery -A celery_app beat --loglevel=info
```

##注意事项
####1.部署时需要新建virtual_host
####2.采用了本地的默认配置和线上nacos配置，优先读取nacos的配置
####3.nacos配置选择yaml格式的配置文件

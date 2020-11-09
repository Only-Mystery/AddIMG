# 部署

以下部署基于 Ubuntu 20.04 和 python 3.8.5。

**注意：部署时将使用root用户**

## AddIMG

1.推荐为 AddIMG 单独创建一个用户。

```
groupadd addimg
useradd -s /sbin/nologin -M -g addimg addimg
```

2.选择一个文件夹放置 AddIMG。（例如：`/opt`）

```
cd /opt
git clone https://github.com/veoco/AddIMG.git
```

3.放置你的图片文件夹

默认的图片文件夹在 AddIMG 的 `images` 目录中。但你可以在 `config.py` 中自己修改路径。

现在你的目录应该看起来像这样：

```
/opt
`-- AddIMG
    |-- LICENSE
    |-- README.md
    |-- bottle.py
    |-- config.py
    |-- deploy.md
    |-- images
    |   `-- test.jpg
    |-- main.py
    `-- tests.py
```

4.修改文件夹拥有者

这可能会阻止潜在的安全风险并可以保证程序正确运行。

```
chown -R addimg:addimg /opt/AddIMG
```

## Python 环境

大多数时候 Python 都会使用单独的虚拟环境，但为了方便我们也可以直接使用系统环境。

1.安装 pip3

我们使用 pip3 安装依赖。

```
apt-get install python3-pip
```

2.安装依赖项

我们需要安装 Pillow 和 Gunicorn。Bottle 已经包含在 AddIMG 项目中。

```
pip3 install pillow gunicorn
```

## Gunicorn 与 Systemd

我们使用 Gunicorn 部署 AddIMG，并且使用 Systemd 管理 Gunicorn 进程。

1.`addimg.service`

```
nano /etc/systemd/system/addimg.service
```

复制粘贴以下配置：

```
[Unit]
Description=addimg daemon
Requires=addimg.socket
After=network.target

[Service]
Type=notify
User=addimg
Group=addimg
RuntimeDirectory=gunicorn
WorkingDirectory=/opt/AddIMG
ExecStart=/usr/local/bin/gunicorn -w2 main:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

**注意：-w? 应该是你CPU核数的两倍**

2.`addimg.socket`

```
nano /etc/systemd/system/addimg.socket
```

复制粘贴以下配置：

```
[Unit]
Description=addimg socket

[Socket]
ListenStream=/tmp/addimg.sock
SocketUser=www-data

[Install]
WantedBy=sockets.target
```

3.开启 Systemd

```
systemctl enable addimg.socket
systemctl enable addimg
systemctl start addimg
```

## Nginx 配置

我们使用 Nginx 处理正常图片, 当图片不存在时，再通过 AddIMG 来处理。

1.安装 Nginx

```
apt-get install nginx
```

2.添加配置

```
nano /etc/nginx/sites-enabled/addimg.conf
```

复制粘贴以下配置，你需要对配置文件修改以适应你自己的网站。

```
upstream app_server {
    server unix:/tmp/addimg.sock fail_timeout=0;
    }

server {
    listen       80;
    server_name  img.addfn.cn;
    return       301 https://img.addfn.cn$request_uri;
}

server {
    listen 443 ssl;
    listen [::]:443 ssl;

    server_name img.addfn.cn;

    ssl_certificate     /home/ssl/img.addfn.cn.crt;
    ssl_certificate_key /home/ssl/img.addfn.cn.key;

    client_max_body_size 0;
    root /opt/AddIMG/images;

    location / {
        try_files $uri @proxy_to_app;
    }

    location @proxy_to_app {
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_pass http://app_server;
    }
}
```

3.重新加载 Nginx

你可以使用以下命令测试 `addimg.conf`：

```
nginx -t
```

如果没有问题，重新加载 Nginx。

```
nginx -s reload
```
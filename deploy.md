# Deployment

The following deployment is based on Ubuntu 20.04 and python 3.8.5.

**NOTE: We will use root user during deployment!**

## AddIMG

1.It's recommened to create a separate account for AddIMG.

```
groupadd addimg
useradd -s /sbin/nologin -M -g addimg addimg
```

2.Select a folder to place the AddIMG.(Example: `/opt`)

```
cd /opt
git clone https://github.com/veoco/AddIMG.git
```

3.Place your image files.

Default folder is the `images` in your AddIMG directory. But you can change this path in the `config.py`.

Your directory should look like:

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

4.Change directory ownner

This can prevent potential security risks and make sure the program runs properly.

```
chown -R addimg:addimg /opt/AddIMG
```

## Python environment

Most of the time Python projects will use a separate virtual environment, but for convenience you can use the system environment.

1.Install pip3

We use pip3 to install our requirements.

```
apt-get install python3-pip
```

2.Install requirements

We need to install Pillow and Gunicorn. The bottle has been included in AddIMG project.

```
pip3 install pillow gunicorn
```

## Gunicorn with Systemd

We will deploy AddIMG by Gunicorn, and use Systemd to manage Gunicorn process.

1.`addimg.service`

```
nano /etc/systemd/system/addimg.service
```

Copy and paste follow configs:

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

**NOTE: -w? should be twice of your cpu cores**

2.`addimg.socket`

```
nano /etc/systemd/system/addimg.socket
```

Copy and paste follow configs:

```
[Unit]
Description=addimg socket

[Socket]
ListenStream=/tmp/addimg.sock
SocketUser=www-data

[Install]
WantedBy=sockets.target
```

3.Enable Systemd

```
systemctl enable addimg.socket
systemctl enable addimg
systemctl start addimg
```

## Nginx configuration

We use Nginx to serve normal images, and if the image is not found, then our program will process the request.

1.Install Nginx

```
apt-get install nginx
```

2.Add conf

```
nano /etc/nginx/sites-enabled/addimg.conf
```

Copy and paste follow configs, and you must change the configs to fit your website!

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

3.Reload nginx

You can test your `addimg.conf` by:

```
nginx -t
```

If there is no problem, reload the nginx:

```
nginx -s reload
```
# Paper-Hub: An easy way to read and share papers for scientific research

## Installation

1. Prepare virtual environment (venv):

```sh
python -m venv venv
. venv/bin/activate
pip install requests django python-decouple xmltodict
```

2. Prepare static files:

```
python manager collectstatic
```

3. Configure Apache (take '/var/www/paper-hub.cn/' as example):

```txt
WSGIApplicationGroup %{GLOBAL}
WSGIDaemonProcess paperhub python-home=/var/www/paper-hub.cn/venv python-path=/var/www/paper-hub.cn
WSGIProcessGroup paperhub
WSGIScriptAlias / /var/www/paper-hub.cn/paperhub/wsgi.py
<Directory /var/www/paper-hub.cn/paperhub/>
    <Files wsgi.py>
        Require all granted
    </Files>
</Directory>
Alias /static /var/www/paper-hub.cn/static_root
<Directory /var/www/paper-hub.cn/static_root/>
    Options -Indexes
    Require all granted
</Directory>
```

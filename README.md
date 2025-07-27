# Paper-Hub

An easy way to read and share papers for scientific research

## 项目结构

```
paper-hub.cn/
├── frontend/          # Vue.js + Vite 前端
├── backend/           # Django 后端
├── dev.sh            # 开发环境启动脚本
└── README.md
```

## Quick Start

### 方法一：使用开发脚本（推荐）

```sh
./dev.sh
```

这将自动：
1. 设置Python虚拟环境
2. 安装后端依赖
3. 运行数据库迁移
4. 启动Django后端服务器 (http://localhost:8000)
5. 安装前端依赖
6. 启动Vue.js前端服务器 (http://localhost:5173)

### 方法二：手动启动

#### 后端设置

1. 准备虚拟环境：

    ```sh
    python -m venv .venv
    source .venv/bin/activate
    cd backend
    pip install -r requirements.txt
    ```

2. 准备静态文件：

    ```sh
    python manage.py collectstatic
    ```

3. 建立数据库：

    ```sh
    python manage.py migrate
    ```

4. 运行后端服务器：

    ```sh
    python manage.py runserver
    ```

#### 前端设置

1. 安装依赖：

    ```sh
    cd frontend
    npm install
    ```

2. 启动开发服务器：

    ```sh
    npm run dev
    ```

## 开发说明

- **前端**: Vue.js 3 + TypeScript + Vite
- **后端**: Django + SQLite/PostgreSQL
- **API**: 使用现有的Django API端点，通过Vite代理转发
- **数据库**: 支持SQLite（开发）和PostgreSQL（生产）

## 访问地址

- 前端应用: http://localhost:5173
- 后端API: http://localhost:8000
- Django管理后台: http://localhost:8000/admin

## Run on Apache HTTP Server

1. Configure Apache (take '/var/www/paper-hub.cn/' as example):

    ```txt
    WSGIApplicationGroup %{GLOBAL}
    WSGIDaemonProcess paperhub python-home=/var/www/paper-hub.cn/.venv python-path=/var/www/paper-hub.cn/backend
    WSGIProcessGroup paperhub
    WSGIScriptAlias / /var/www/paper-hub.cn/backend/mysite/wsgi.py
    WSGIPassAuthorization On
    <Directory /var/www/paper-hub.cn/backend/mysite/>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>
    Alias /static /var/www/paper-hub.cn/backend/static_root
    <Directory /var/www/paper-hub.cn/backend/static_root/>
        Options -Indexes
        Require all granted
    </Directory>
    ```

2. Configure server side for mini program

    ```sh
    $ cat .env
    OPENAI_API_KEY=sk-xxxxxx
    OPENAI_PROXY_URL=xxxxxx

    WX_APP_ID=wxxxxx
    WX_SECRET=xxxxxx
    WX_DEBUG=False

    WEB_APP_ID=wxxxxx
    WEB_APP_SECRET=xxxxxx
    WEB_DOMAIN=paper-hub.cn

    AZURE_KEY=xxxxxx
    AZURE_ENDPOINT=https://api.cognitive.microsofttranslator.com
    AZURE_LOCATION=eastus
    AZURE_PATH=/translate

    PUBMED_DIR=/path/to/pubmed/

    DB_NAME=xxxx
    DB_USER=xxxx
    DB_PASSWORD=xxxx
    DB_HOST=xxxx

    DEV_DB_NAME=xxxx
    DEV_DB_USER=xxxx
    DEV_DB_PASSWORD=xxxx
    DEV_DB_HOST=xxxx

    LOCAL_DB_NAME=xxxx
    LOCAL_DB_USER=xxxx
    LOCAL_DB_PASSWORD=xxxx
    LOCAL_DB_HOST=xxxx

    DJANGO_ENV=production # production / development / local / sqlite
    ```

## How to setup a development environment (Optional)

1. Start Django application locally.

    ```sh
    # run this command in a separated terminal
    . .venv/bin/activate
    cd backend
    python manage.py runserver
    ```

2. Use SSH start to reverse tunnel (take 'paper-hub.cn' as an example).

    ```sh
    # run this command in another new terminal
    ssh -nNT -R *:8000:localhost:8000 paper-hub.cn
    ```

    This will map 8000 port on remote server to 8000 port on local machine.

    On remote server, `/etc/ssh/sshd_config` should set the option:

    ```txt
    GatewayPorts yes
    ```

3. Configure Apache on remote server.

    ```txt
    <VirtualHost *:8443>
        ...
        SSLEngine on
        SSLCertificateFile /path/to/.../fullchain.pem
        SSLCertificateKeyFile /path/to/.../privkey.pem

        ProxyPass / http://127.0.0.1:8000/
        ProxyPassReverse / http://127.0.0.1:8000/
        ...
    </VirtualHost>
    </IfModule>
    ```

    This will open 8443 port as https server, and map the request/response to 8000 on remote server.

4. After all these, port 8443 on the remote server could be accessed as <https://paper-hub.cn:8443/>, which could be set as a safe domain in Mini Program development.


## FAQ

1. **Q:** How do I configure a SOCKS5 proxy server when installing packages with pip?

    **A:** Before calling pip install, define the environment variable ALL_PROXY:

    ```sh
    export ALL_PROXY=socks5://xxx.xxx.xxx.xxx:1090
    ```

2. **Q:** What should I do if I encounter the following error during installation:

    ```
    ERROR: Could not install packages due to an OSError: Missing dependencies for SOCKS support.
    ```

    **A:** You need to remove the proxy configuration first, install the PySocks package, and then use the proxy again:

    ```sh
    pip install PySocks
    ```

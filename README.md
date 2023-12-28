# Paper-Hub

An easy way to read and share papers for scientific research

## Installation

1. Prepare virtual environment (venv):

    ```sh
    python -m venv venv
    . venv/bin/activate
    pip install django
    pip install python-dotenv
    pip install requests
    pip install xmltodict
    pip install openai
    pip install socksio
    pip install PySocks
    ```

2. Prepare static files:

    ```sh
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

4. Configure server side for mini program

    ```sh
    $ cat .env
    OPENAI_API_KEY=sk-xxxxxx
    OPENAI_PROXY_URL=xxxxxx
    WX_APP_ID=xxxxxx
    WX_SECRET=xxxxxx
    ```

## How to setup a development environment (Optional)

1. Start Django application locally.

    ```sh
    # run this command in a separated terminal
    . venv/bin/activate
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

# Paper-Hub

An easy way to read and share papers for scientific research

## Quick Start

1. Setup environment (install dependencies and node packages):

    ```sh
    ./scripts/setup.sh
    ```

    Or manually:

    ```sh
    uv sync --no-install-project
    npm install
    npm run build
    ```

2. Prepare static files:

    ```sh
    uv run python manage.py collectstatic
    ```

3. Establish database:

    ```sh
    uv run python manage.py migrate
    ```

4. Run Server:

    ```sh
    uv run python manage.py runserver
    ```

    Note: Using `uv run` automatically uses the virtual environment, no need to activate it manually. Alternatively, you can activate the environment with `source .venv/bin/activate` and use `python` directly.

## Run on Apache HTTP Server

1. Configure Apache (take '/var/www/paper-hub.cn/' as example):

    ```txt
    WSGIApplicationGroup %{GLOBAL}
    WSGIDaemonProcess paperhub python-home=/var/www/paper-hub.cn/.venv python-path=/var/www/paper-hub.cn
    WSGIProcessGroup paperhub
    WSGIScriptAlias / /var/www/paper-hub.cn/config/wsgi.py
    WSGIPassAuthorization On
    <Directory /var/www/paper-hub.cn/config/>
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
    uv run python manage.py runserver
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

1. **Q:** How do I configure a SOCKS5 proxy server when installing packages with uv?

    **A:** Before calling `uv sync`, define the environment variable ALL_PROXY:

    ```sh
    export ALL_PROXY=socks5://xxx.xxx.xxx.xxx:1090
    uv sync
    ```

2. **Q:** How do I upgrade dependencies to the latest versions?

    **A:** Use `uv lock --upgrade` to update the lock file, then `uv sync`:

    ```sh
    uv lock --upgrade
    uv sync
    ```

    Or upgrade a specific package:

    ```sh
    uv lock --upgrade-package <package>
    uv sync
    ```

3. **Q:** How do I generate or update the lock file?

    **A:** Use `uv lock` command:

    ```sh
    uv lock
    ```

    This will resolve dependencies from `pyproject.toml` and generate/update `uv.lock` file.

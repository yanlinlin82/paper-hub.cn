# Paper-Hub

An easy way to read and share papers for scientific research

## Project Split (2026)

This repository is being simplified to keep only:

- community display pages (`/group/...`)
- admin login and content editing (`/admin/...`)

Non-community features are being moved to a sibling repository:

- `../paper-tracker`

Literature tracking/recommendation/chat data models have been removed from this repository to keep only community workflows.

## Project Structure

```
paper-hub.cn/
├── backend/              # Django / Python backend
│   ├── api/              #   REST API app
│   ├── config/           #   Django project settings & URL routing
│   ├── core/             #   Core data models
│   ├── group/            #   Group pages (redirects to SPA)
│   ├── scripts/          #   Utility scripts
│   ├── static/           #   Static file sources
│   ├── static_root/      #   Collected static files (collectstatic)
│   ├── media/            #   User-uploaded media
│   ├── logs/             #   Application logs
│   ├── cache/            #   API response cache
│   ├── logo/             #   Brand assets
│   ├── db.sqlite3        #   SQLite database
│   ├── pyproject.toml    #   Python dependencies
│   ├── uv.lock           #   Lock file for uv
│   └── manage.py         #   Django management script
├── frontend/             # React SPA (Vite)
│   ├── src/              #   Source code
│   ├── public/           #   Static assets
│   └── dist/             #   Build output
├── docker/               # Docker / Nginx configs
│   ├── backend/
│   ├── frontend/
│   └── nginx/
├── docker-compose.yml    # Dev environment (single-port)
└── README.md
```

## Community Data Maintenance

This repository keeps only community check-in data.

Use the unified script below to inspect cleanup impact, export a deterministic JSON snapshot, or import one back (run from `backend/`):

```sh
cd backend
uv run python scripts/community-data.py cleanup
uv run python scripts/community-data.py cleanup --run

uv run python scripts/community-data.py export ./community-data.json

uv run python scripts/community-data.py import ./community-data.json
uv run python scripts/community-data.py import ./community-data.json --run
```

Notes:

- `cleanup` deletes personal literature data that is not linked to any group review.
- `cleanup` and `import` default to dry-run mode. Add `--run` to write changes.
- `export` writes pretty JSON with sorted keys so identical data exports to identical file content.

## Quick Start

All backend commands below must be run from the `backend/` directory:

```sh
cd backend
```

1. Setup environment (install Python dependencies and node packages):

    ```sh
    ./scripts/setup.sh
    ```

    Or manually:

    ```sh
    uv sync
    cd ../frontend
    npm install
    npm run build
    cd ../backend
    ```

2. Prepare static files:

    ```sh
    uv run python manage.py collectstatic
    ```

3. Establish database:

    ```sh
    uv run python manage.py migrate
    ```

4. Run development server:

    ```sh
    uv run python manage.py runserver
    ```

    Note: Using `uv run` automatically uses the virtual environment, no need to activate it manually. Alternatively, you can activate the environment with `source .venv/bin/activate` (after creating it with `uv sync` in the `backend/` directory) and use `python` directly.

### Docker (alternative)

Run the whole stack (backend + frontend + nginx) with a single command:

```sh
docker compose up -d
# Visit http://localhost:8000
```

## Run on Apache HTTP Server

1. Configure Apache (take '/var/www/paper-hub.cn/' as example, note the `backend/` prefix in paths):

    ```txt
    WSGIApplicationGroup %{GLOBAL}
    WSGIDaemonProcess paperhub python-home=/var/www/paper-hub.cn/backend/.venv python-path=/var/www/paper-hub.cn/backend
    WSGIProcessGroup paperhub
    WSGIScriptAlias / /var/www/paper-hub.cn/backend/config/wsgi.py
    WSGIPassAuthorization On
    <Directory /var/www/paper-hub.cn/backend/config/>
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

1. Start Django application locally (from `backend/` directory).

    ```sh
    cd backend
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

    **A:** Before calling `uv sync`, define the environment variable ALL_PROXY. Run all `uv` commands from the `backend/` directory:

    ```sh
    cd backend
    export ALL_PROXY=socks5://xxx.xxx.xxx.xxx:1090
    uv sync
    ```

2. **Q:** How do I upgrade dependencies to the latest versions?

    **A:** Use `uv lock --upgrade` to update the lock file, then `uv sync` (run from `backend/`):

    ```sh
    cd backend
    uv lock --upgrade
    uv sync
    ```

    Or upgrade a specific package:

    ```sh
    cd backend
    uv lock --upgrade-package <package>
    uv sync
    ```

3. **Q:** How do I generate or update the lock file?

    **A:** Use `uv lock` command (run from `backend/`):

    ```sh
    cd backend
    uv lock
    ```

    This will resolve dependencies from `pyproject.toml` and generate/update `uv.lock` in the `backend/` directory.

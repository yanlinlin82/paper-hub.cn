# Paper-Hub

An easy way to read and share papers for scientific research.

## Quick Start

The entire stack (backend + frontend + nginx) runs via Docker Compose.
Only the nginx reverse proxy port is exposed — all services communicate
over an internal Docker network.

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- `node` (v18+) — only needed to run the npm script wrapper, not for the services themselves

### Start the services

```sh
npm run dev
```

Or equivalently:

```sh
docker compose up
```

Visit **http://localhost:8000**.

### Custom port

Override the exposed port via `DEV_PORT`:

```sh
DEV_PORT=8001 npm run dev
# or
DEV_PORT=8001 docker compose up
```

## Scripts reference

All commands run from the project root.

### Development

| Command | Description |
|---|---|
| `npm run dev` | Start all services (foreground) |
| `npm run dev:up` | Start all services (background) |
| `npm run dev:down` | Stop all containers |
| `npm run dev:build` | Rebuild Docker images |
| `npm run dev:logs` | Tail logs from all services |
| `npm run dev:ps` | List running containers |

### Lifecycle

| Command | Description |
|---|---|
| `npm run setup` | Initialize environment — install Python deps (`uv sync`) and npm packages |
| `npm run check` | Run code checks — Django system check (`manage.py check`) and frontend lint (`eslint`) |
| `npm run test` | Run backend tests (`manage.py test`) |
| `npm run build` | Build for deployment — build SPA (`frontend/dist/`) and collect static files (`backend/static_root/`) |

The `setup` script must be run before `check`, `test`, or `build`, and `build` must be run before deploying the artifacts to another server.

### Python venv

The Python virtual environment lives at `backend/.venv` and is shared
between your host machine and the backend container via a bind mount.
This lets you run Django management commands both on the host and
inside the container using the same environment.

`uv sync` is only ever run on the **host** — the Docker image and
container never install Python dependencies.

**First time setup (required before starting containers):**

```sh
cd backend
uv sync
```

This creates `backend/.venv` with all Python dependencies installed.
When you later run `npm run dev`, the bind mount `./backend:/app` shares
this `.venv` into the container at `/app/.venv`, and `uv run` inside the
container picks it up automatically.

> ⚠️ If you start the containers without a host `backend/.venv`, the
> backend container will fail to start because `uv run` cannot find the
> required dependencies.

**Common host-side commands:**

```sh
cd backend
uv run python manage.py makemigrations    # create DB migrations
uv run python manage.py migrate            # apply migrations
uv run python manage.py collectstatic      # collect static files
uv run python manage.py createsuperuser    # create an admin user
uv add <package>                           # add a new dependency
uv lock --upgrade                          # upgrade all dependencies
```

### Environment (docker)

Create a `.env.docker` file in the project root with any overrides needed.
A template is created automatically on first startup if it doesn't exist.

Common environment variables include `OPENAI_API_KEY`, `WEIXIN_APP_ID`, etc.

## Architecture

```
                       ┌──────────────┐
                       │   Browser     │
                       │ :8000         │
                       └──────┬───────┘
                              │
                       ┌──────▼───────┐
                       │   Nginx      │  ← single entry point
                       │ (port 80)    │
                       └──┬───────┬───┘
                          │       │
                ┌─────────▼─┐  ┌──▼──────────┐
                │  Backend   │  │  Frontend    │
                │  Django    │  │  Vite dev    │
                │  :8000     │  │  :5173       │
                └────────────┘  └──────────────┘
```

- `/admin/`, `/api/`, `/static/` → proxied to the Django backend
- Everything else (`/`, `/group/...`, etc.) → proxied to the Vite dev server (SPA with HMR)

## FAQ

**1. Q:** How do I run a Django management command inside the backend container?

**A:**

```sh
docker compose exec backend uv run python manage.py <command>
```

For example, to create a superuser:

```sh
docker compose exec backend uv run python manage.py createsuperuser
```

**2. Q:** How do I install a new npm package?

**A:** The frontend container uses a bind mount, so changes to `package.json` are
picked up. Run:

```sh
docker compose exec frontend npm install <package>
```

Then restart the container to reinstall from the updated lock file:

```sh
docker compose restart frontend
```

**3. Q:** How do I configure a SOCKS5 proxy for pip/uv inside the container?

**A:** Set `ALL_PROXY` in `.env.docker`:

```
ALL_PROXY=socks5://xxx.xxx.xxx.xxx:1090
```

**4. Q:** How do I upgrade Python dependencies?

**A:** Edit `backend/pyproject.toml`, then from the backend container:

```sh
docker compose exec backend uv lock --upgrade
docker compose exec backend uv sync
```

**5. Q:** How do I set up a reverse SSH tunnel for WeChat Mini Program development?

**A:** Start the stack, then tunnel from your remote server:

```sh
ssh -nNT -R *:8000:localhost:8000 your-server
```

On the remote server, configure Apache/Nginx to proxy `/` to `127.0.0.1:8000` and enable HTTPS.

**6. Q:** How do I generate or update the uv lock file?

**A:** From inside the backend container:

```sh
docker compose exec backend uv lock
```

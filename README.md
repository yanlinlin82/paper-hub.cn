# Paper-Hub

An easy way to read and share papers for scientific research.

## Quick Start

The entire stack (backend + frontend + nginx) runs via Docker Compose.
Only the nginx reverse proxy port is exposed — all services communicate
over an internal Docker network.

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- `node` (v22.22+, used by the frontend build) — on the host only needed to run the npm script wrapper, not for the services themselves

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

### Member reading-interest report

Generates per-member reading-interest profiles from the group's paper reviews
(check-ins) using an LLM (DeepSeek), and exposes them on the website at
`/group/:groupName/member-report` where each member is clickable.

**Prerequisite** — an API key in `backend/.env` (copy the committed template):

```sh
cd backend
cp .env.example .env
# then set DEEPSEEK_API_KEY=sk-xxxx in backend/.env
```

**Generate the report:**

```sh
cd backend
uv run manage.py generate_member_report --group xiangma
```

The command requires `DEEPSEEK_API_KEY` to be set and calls `deepseek-v4-flash`
(the current DeepSeek chat model; override with `LLM_MODEL` if it changes). It
fails fast if the key is missing or the API is unreachable, instead of quietly
falling back to template text. Each member profile is generated from up to 30 of
their own reviews, taking advantage of the model's large context window. It needs
`max_tokens` budget so the reasoning model does not truncate the answer to empty.

It generates profiles concurrently (`--workers`, default 4) and writes each
member's file as soon as it succeeds, so a failed member can be re-run on its
own later with `--user <id>`. It pauses `--delay` seconds between completions
(default 1.0; `--delay 0` disables) and retries transient failures with backoff
so it stays under DeepSeek's rate limit. Lower `--workers` (or raise `--delay`)
if you hit rate-limit errors.

Output is written under `backend/reports/` (gitignored):

- `<group>_member_report.json` — the group index: aggregate stats plus a
  lightweight member list.
- `<group>_members/<user_id>.json` — one file per member holding that member's
  full profile, so a single member can be read or regenerated independently
  (`--user <id>`).
- `<group>_member_report.html` — a standalone, shareable HTML report.

The website index (`/api/groups/<group>/member-report/`) serves the index; the
full per-member profile is fetched lazily from
`/api/groups/<group>/member-report/<user_id>/`.

The report also persists a topic → reviews mapping (`<group>_topics.json`), which
powers the topic list page `/group/<group>/member-report/topic/:topic` (served by
`/api/groups/<group>/member-report/topics/:topic/`). Clicking a topic tag in the
member profiles or the profile dialog navigates there and lists every review in
that research topic (whole group).

Member tiers are based on check-in frequency plus activity (so members who joined
at different times are compared fairly): 高频 (active and ≥2 reviews/month),
坚持 (active and ≥1 review/month), 稀疏 (active but <1 review/month), 尝试
(active but only 1 review total), 暂停 (no check-in this month or last).

### Database backup

`backend/scripts/daily-update.sh` only backs up the database — it no longer
performs any data updates. It copies `backend/db.sqlite3` to a date-stamped
file (`db.sqlite3.bak-YYYYMMDD`) and keeps only the 7 most recent backups.

Run it from a crontab on the production server.

### Environment (docker)

`.env.docker` is required at the project root — `docker-compose.yml` references
it via `env_file`, and the stack will not start if the file is missing.
Its default values cover local development only; add any overrides you need.

Common environment variables include `OPENAI_API_KEY`, `WEIXIN_APP_ID`, `ALL_PROXY`, etc.

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

**7. Q:** How do I update the deployed code?

**A:** On the production server:

```sh
git pull
npm run build
touch backend/config/wsgi.py
```

- `git pull` — fetch the latest source.
- `npm run build` — rebuild the SPA (`frontend/dist/`) and collect static files (`backend/static_root/`).
- `touch backend/config/wsgi.py` — bump the file mtime so Apache mod_wsgi reloads the Django app on the next request.

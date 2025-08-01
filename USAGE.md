# Paper Hub - Quick Start

## Setup & Development

```bash
# Initial setup
npm run setup

# Start development (both frontend & backend)
npm run dev

# Start frontend only
npm run dev:frontend

# Start backend only
npm run dev:backend
```

## Common Commands

```bash
npm run setup:upgrade    # Update dependencies
npm run build           # Build frontend
npm run test            # Run tests
npm run lint            # Check code
npm run format          # Format code
npm run migrate         # Run migrations
npm run shell           # Django shell
```

## Access URLs

- **Frontend**: http://localhost:5173
- **Backend**: http://localhost:8000
- **Admin**: http://localhost:8000/admin

## Note

The `npm run dev` command starts both servers concurrently using bash background processes. Use `Ctrl+C` to stop both servers.

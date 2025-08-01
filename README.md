# Paper Hub

Academic paper management system built with Django and Vue.js.

## Quick Start

### Prerequisites

- Node.js >= 18.0.0
- npm >= 9.0.0
- Python >= 3.8
- pip

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd paper-hub
   ```

2. **Setup the project**

   ```bash
   npm run setup
   ```

   This will:
   - Install frontend dependencies (Vue.js)
   - Create and activate Python virtual environment
   - Install backend dependencies (Django)

3. **Start development servers**

   ```bash
   npm run dev
   ```

   This will start both frontend (Vite dev server) and backend (Django development server) concurrently.

## Available Commands

### Setup Commands

| Command | Description |
|---------|-------------|
| `npm run setup` | Setup both frontend and backend (use lock files) |
| `npm run setup:upgrade` | Setup with latest versions (ignore lock files) |

### Development Commands

| Command | Description |
|---------|-------------|
| `npm run dev` | Start both frontend and backend development servers |
| `npm run dev:frontend` | Start frontend development server only |
| `npm run dev:backend` | Start backend development server only |

### Build & Test Commands

| Command | Description |
|---------|-------------|
| `npm run build` | Build frontend for production |
| `npm run test` | Run frontend tests |
| `npm run lint` | Lint frontend code |
| `npm run format` | Format frontend code |

### Django Commands

| Command | Description |
|---------|-------------|
| `npm run migrate` | Run Django migrations |
| `npm run shell` | Open Django shell |

## Project Structure

```txt
paper-hub/
├── frontend/          # Vue.js frontend application
│   ├── src/          # Source code
│   ├── public/       # Static assets
│   └── package.json  # Frontend dependencies
├── backend/          # Django backend application
│   ├── api/          # API views and serializers
│   ├── core/         # Core Django settings
│   ├── .venv/        # Python virtual environment
│   └── requirements.txt  # Python dependencies
├── scripts/          # Utility scripts
│   └── setup.sh      # Setup script
└── package.json      # Root package.json with npm scripts
```

## Development Workflow

1. **Initial Setup**

   ```bash
   npm run setup
   ```

2. **Start Development**

   ```bash
   npm run dev
   ```

3. **Make Changes**
   - Frontend: Edit files in `frontend/src/`
   - Backend: Edit files in `backend/`

4. **Code Quality**

   ```bash
   npm run format  # Format code
   npm run lint    # Check code quality
   ```

5. **Testing**

   ```bash
   npm run test    # Run all tests
   ```

## Environment Variables

### Backend (.env file in backend/ directory)

```txt
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///db.sqlite3
```

### Frontend (.env file in frontend/ directory)

```txt
VITE_API_BASE_URL=http://localhost:8000/api
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

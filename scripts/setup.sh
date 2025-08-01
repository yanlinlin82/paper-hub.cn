#!/bin/bash

# Paper Hub Setup Script
# Used to initialize and install necessary dependencies for frontend and backend

set -e  # Exit on error

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Show help information
show_help() {
    cat << EOF
Paper Hub Setup Script

Usage: $0 [options]

Options:
    -h, --help      Show this help message
    -u, --upgrade   Force upgrade to latest versions (ignore lock files)
    -f, --frontend  Setup frontend only
    -b, --backend   Setup backend only

Examples:
    $0              # Normal setup (use lock files)
    $0 -u           # Force upgrade to latest versions
    $0 -f           # Setup frontend only
    $0 -b -u        # Setup backend only and force upgrade

EOF
}

# Check if command exists
check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "Command '$1' not found, please install it first"
        exit 1
    fi
}

# Check frontend lock file
check_frontend_lock() {
    if [[ -f "frontend/package-lock.json" ]]; then
        log_info "Found package-lock.json, will use locked versions"
        return 0
    else
        log_warning "No package-lock.json found, will install latest versions"
        return 1
    fi
}

# Check backend lock files
check_backend_lock() {
    if [[ -f "backend/requirements.txt" ]] || [[ -f "backend/requirements_dev.txt" ]]; then
        log_info "Found requirements.txt or requirements_dev.txt, will use locked versions"
        return 0
    else
        log_warning "No lock files found, will install latest versions"
        return 1
    fi
}

# Setup frontend dependencies
setup_frontend() {
        log_info "Starting frontend dependency setup..."

    if [[ ! -d "frontend" ]]; then
        log_error "frontend directory does not exist"
        return 1
    fi

    cd frontend

    # Check if upgrade is needed
    local should_upgrade=false
    if [[ "$FORCE_UPGRADE" == "true" ]]; then
        should_upgrade=true
        log_info "Force upgrade mode: will install latest versions"
    elif ! check_frontend_lock; then
        should_upgrade=true
    fi

        if [[ "$should_upgrade" == "true" ]]; then
        log_info "Removing package-lock.json (if exists)..."
        rm -f package-lock.json
    fi

    log_info "Running npm install..."
    if npm install; then
        log_success "Frontend dependencies installed successfully"
    else
        log_error "Frontend dependency installation failed"
        return 1
    fi

    cd ..
}

# Setup backend dependencies
setup_backend() {
        log_info "Starting backend dependency setup..."

    if [[ ! -d "backend" ]]; then
        log_error "backend directory does not exist"
        return 1
    fi

    cd backend

        # Check virtual environment
    if [[ ! -d ".venv" ]]; then
        log_info "Creating virtual environment..."
        python3 -m venv .venv
    fi

    # Activate virtual environment
    log_info "Activating virtual environment..."
    source .venv/bin/activate

    # Upgrade pip
    log_info "Upgrading pip..."
    pip install --upgrade pip

    # Check if upgrade is needed
    local should_upgrade=false
    if [[ "$FORCE_UPGRADE" == "true" ]]; then
        should_upgrade=true
        log_info "Force upgrade mode: will install latest versions"
    elif ! check_backend_lock; then
        should_upgrade=true
    fi

        if [[ "$should_upgrade" == "true" ]]; then
        log_info "Installing dependencies from .in files..."

        # Install production dependencies
        if [[ -f "requirements.in" ]]; then
            log_info "Installing production dependencies..."
            pip install -r requirements.in
        fi

        # Install development dependencies
        if [[ -f "requirements_dev.in" ]]; then
            log_info "Installing development dependencies..."
            pip install -r requirements_dev.in
        fi

        # Generate lock files
        log_info "Generating lock files..."
        pip freeze > requirements.txt
        pip freeze > requirements_dev.txt
        else
        log_info "Installing dependencies from lock files..."

        # Prefer requirements_dev.txt, fallback to requirements.txt
        if [[ -f "requirements_dev.txt" ]]; then
            log_info "Installing development dependencies (includes production dependencies)..."
            pip install -r requirements_dev.txt
        elif [[ -f "requirements.txt" ]]; then
            log_info "Installing production dependencies..."
            pip install -r requirements.txt
        else
            log_error "No dependency files found"
            return 1
        fi
    fi

    log_success "Backend dependencies installed successfully"
    cd ..
}

# Main function
main() {
        log_info "Paper Hub setup script starting..."

    # Check required commands
    check_command "npm"
    check_command "python3"

    # Parse command line arguments
    FORCE_UPGRADE=false
    SETUP_FRONTEND=true
    SETUP_BACKEND=true

    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -u|--upgrade)
                FORCE_UPGRADE=true
                shift
                ;;
            -f|--frontend)
                SETUP_FRONTEND=true
                SETUP_BACKEND=false
                shift
                ;;
            -b|--backend)
                SETUP_FRONTEND=false
                SETUP_BACKEND=true
                shift
                ;;
            *)
                log_error "Unknown argument: $1"
                show_help
                exit 1
                ;;
        esac
    done

        # Log setup mode
    if [[ "$FORCE_UPGRADE" == "true" ]]; then
        log_info "Mode: Force upgrade to latest versions"
    else
        log_info "Mode: Use locked versions (if available)"
    fi

    # Setup frontend
    if [[ "$SETUP_FRONTEND" == "true" ]]; then
        setup_frontend
    fi

    # Setup backend
    if [[ "$SETUP_BACKEND" == "true" ]]; then
        setup_backend
    fi

    log_success "Paper Hub setup completed!"

    # Show next steps
    echo
    log_info "Next steps:"
    if [[ "$SETUP_FRONTEND" == "true" ]]; then
        echo "  Frontend: cd frontend && npm run dev"
    fi
    if [[ "$SETUP_BACKEND" == "true" ]]; then
        echo "  Backend: cd backend && source .venv/bin/activate && python manage.py runserver"
    fi
}

# Execute main function
main "$@"

# flake.nix - Nix Flake configuration for Courier Feedback System
# This creates a reproducible development environment with Python and Node.js
# for building offline-first feedback apps with Reflex + Jazz CRDT sync
{
  description = "Courier Feedback System - Offline-first delivery feedback app with Reflex + Jazz";

  # Inputs are external dependencies for our flake
  inputs = {
    # nixpkgs is the main package repository for Nix
    # Using "nixos-unstable" gives us the latest packages
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

    # flake-utils helps us write flakes that work on multiple systems
    flake-utils.url = "github:numtide/flake-utils";
  };

  # Outputs define what our flake produces
  outputs = { self, nixpkgs, flake-utils }:
    # Create outputs for each system (x86_64-linux, aarch64-darwin, etc.)
    flake-utils.lib.eachDefaultSystem (system:
      let
        # Import nixpkgs for our specific system
        pkgs = nixpkgs.legacyPackages.${system};

        # Define Python packages we want available in the environment
        pythonPackages = ps: with ps; [
          # Core package management
          pip
          setuptools
          wheel
          
          # Application dependencies (base versions, requirements.txt will override)
          fastapi
          uvicorn
          pydantic
          bcrypt
          python-dotenv
          
          # Testing and development tools
          pytest
          pytest-asyncio
          pytest-cov
          black
          mypy
          flake8
          isort
          
          # Additional utilities
          ipython
          requests
        ];

        # Create a Python environment with our packages
        pythonEnv = pkgs.python311.withPackages pythonPackages;

      in
      {
        # devShells.default is the development environment
        devShells.default = pkgs.mkShell {
          # Packages to include in the shell environment
          buildInputs = with pkgs; [
            pythonEnv
            nodejs_20           # LTS version for stability
            nodePackages.npm
            nodePackages.typescript
            git
            gnumake
            ripgrep
            jq
            curl
            wget
            sqlite              # SQLite for local development
            postgresql          # PostgreSQL for production-like testing
            bandit              # Security linting
          ];

          shellHook = ''
            # Set environment variables
            export PROJECT_NAME="courier-feedback-system"
            export NODE_ENV="development"
            export PYTHONPATH="$PWD:$PYTHONPATH"
            export PIP_USER="0"  # Allow pip to install in nix-shell
            
            # Create virtual environment directory
            export VIRTUAL_ENV=$PWD/.venv
            export PATH="$VIRTUAL_ENV/bin:$PATH"

            echo "🚚 Courier Feedback System - Development Environment"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo "📦 Python $(python --version | cut -d' ' -f2)"
            echo "📦 Node.js $(node --version)"
            echo "📦 npm v$(npm --version)"
            echo "📦 SQLite $(sqlite3 --version | cut -d' ' -f1)"
            echo ""
            echo "🎯 Deployment Mode: $(grep '^APP_MODE=' .env 2>/dev/null | cut -d'=' -f2 || echo 'not configured')"
            echo ""
            echo "🚀 Quick Start:"
            echo "  1. Install dependencies:     pip install -r requirements.txt"
            echo "  2. Copy environment:         cp .env.example .env"
            echo "  3. Run application:          reflex run"
            echo "  4. Run tests:                make test"
            echo ""
            echo "📚 Available Commands:"
            echo "  make dev              - Run development server"
            echo "  make test             - Run all tests"
            echo "  make test-unit        - Run unit tests only"
            echo "  make test-cov         - Run tests with coverage"
            echo "  make lint             - Run linters (flake8, bandit)"
            echo "  make format           - Format code (black, isort)"
            echo "  make clean            - Clean test artifacts"
            echo "  make help             - Show all make commands"
            echo ""
            echo "🌐 Access URLs (when running):"
            echo "  Frontend:  http://localhost:3000"
            echo "  Backend:   http://localhost:8000"
            echo "  Admin:     http://localhost:3000/admin"
            echo ""

            # Create .env if it doesn't exist
            if [ ! -f .env ]; then
              echo "⚠️  No .env file found."
              if [ -f .env.example ]; then
                echo "   Creating from .env.example..."
                cp .env.example .env
                echo "✅ Created .env file (review and customize as needed)"
              else
                echo "❌ .env.example not found - please create .env manually"
              fi
              echo ""
            fi

            # Check if Python dependencies are installed
            if ! python -c "import reflex" 2>/dev/null; then
              echo "📦 Reflex not found. Installing Python dependencies..."
              echo "   This may take a few minutes on first run..."
              pip install -r requirements.txt
              echo "✅ Python dependencies installed"
              echo ""
            fi

            # Create database directory if needed
            mkdir -p $(dirname $(grep '^DATABASE_URL=' .env 2>/dev/null | cut -d'=' -f2 | sed 's|sqlite:///||' | sed 's|./||' || echo "reflx.db"))

            echo "✨ Environment ready! Run 'reflex run' to start the app."
            echo ""
          '';
        };

        # Expose packages for building/deployment
        packages.default = pythonEnv;
      });
}
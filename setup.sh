#!/bin/bash
# MedViz3D — Quick Setup Script
# Run: bash setup.sh

set -e

echo ""
echo "╔═══════════════════════════════════════╗"
echo "║      MedViz3D Setup                   ║"
echo "║  AI Medical Imaging Platform          ║"
echo "╚═══════════════════════════════════════╝"
echo ""

# ── Check Python ──────────────────────────────────
if ! command -v python3 &>/dev/null; then
  echo "❌ Python 3 not found. Install from https://python.org"
  exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "✓ Python $PYTHON_VERSION found"

# ── Check Node ────────────────────────────────────
if ! command -v node &>/dev/null; then
  echo "❌ Node.js not found. Install from https://nodejs.org"
  exit 1
fi
echo "✓ Node $(node --version) found"

# ── Create .env ───────────────────────────────────
if [ ! -f .env ]; then
  cp .env.example .env
  echo ""
  echo "📝 Created .env file"
  echo "   → Add your ANTHROPIC_API_KEY to .env for AI report parsing"
  echo "   → Get one at: https://console.anthropic.com"
else
  echo "✓ .env file exists"
fi

# ── Data directories ──────────────────────────────
mkdir -p data/uploads data/output
echo "✓ Data directories ready"

# ── Backend Python venv ───────────────────────────
echo ""
echo "📦 Setting up Python backend..."
cd backend

if [ ! -d "venv" ]; then
  python3 -m venv venv
  echo "✓ Virtual environment created"
fi

source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "✓ Python dependencies installed"

# Optional: TotalSegmentator (heavy, needs PyTorch)
echo ""
echo "🤖 TotalSegmentator (AI segmentation) is OPTIONAL but recommended."
read -p "   Install now? It downloads ~2GB models (y/N): " install_ts
if [[ "$install_ts" == "y" || "$install_ts" == "Y" ]]; then
  pip install TotalSegmentator -q
  echo "✓ TotalSegmentator installed"
  echo "   Note: First run will download model weights (~2GB)"
else
  echo "   Skipped. Threshold-based segmentation will be used as fallback."
fi

cd ..

# ── Frontend Node deps ────────────────────────────
echo ""
echo "📦 Setting up React frontend..."
cd frontend
npm install --silent
echo "✓ Node dependencies installed"
cd ..

echo ""
echo "╔═══════════════════════════════════════╗"
echo "║  Setup complete! How to start:        ║"
echo "╚═══════════════════════════════════════╝"
echo ""
echo "  Terminal 1 — Backend:"
echo "  cd backend && source venv/bin/activate"
echo "  uvicorn main:app --reload --port 8000"
echo ""
echo "  Terminal 2 — Frontend:"
echo "  cd frontend && npm run dev"
echo ""
echo "  Then open: http://localhost:5173"
echo ""
echo "  OR use Docker (needs Docker installed):"
echo "  docker compose up --build"
echo ""

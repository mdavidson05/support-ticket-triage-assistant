#!/usr/bin/env bash
set -e

if [ -f backend/requirements.txt ]; then
  pip install -r backend/requirements.txt
fi

if [ -f backend/requirements-dev.txt ]; then
  pip install -r backend/requirements-dev.txt
fi

if [ -f frontend/package.json ]; then
  cd frontend
  npm install
  cd ..
fi

python --version
node --version
npm --version
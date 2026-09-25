#!/bin/sh
cd "$(dirname "$0")/core" || exit 1

if [ ! -x venv/bin/python ]; then
  python3 -m venv venv
fi

if ! venv/bin/python -c "import imgui_bundle" >/dev/null 2>&1; then
  venv/bin/pip install imgui-bundle
fi

exec ./venv/bin/python main.py

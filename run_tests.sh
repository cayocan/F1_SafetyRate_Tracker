#!/usr/bin/env bash
set -euo pipefail
# Run the test suite (POSIX)
python -m pytest tests "$@"

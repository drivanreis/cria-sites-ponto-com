# File: csl_file.sh
#!/bin/bash

clear
rm -rf backend/alembic/versions/*
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type d -name ".pytest_cache" -exec rm -rf {} +
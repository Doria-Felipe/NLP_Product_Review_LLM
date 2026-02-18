#!/bin/bash
# deploy.sh — Upload webapp to OVH shared hosting via SFTP
#
# Usage:
#   1. Copy .env.example to .env and fill in your OVH credentials
#   2. Run generate_webapp.py to create the data/ folder
#   3. ./deploy.sh

set -e

# Load config from .env
if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found."
    echo "  Copy .env.example to .env and fill in your credentials:"
    echo "  cp .env.example .env"
    exit 1
fi

source .env

# Validate required vars
if [ -z "$OVH_HOST" ] || [ "$OVH_HOST" = "your-server.ovh.net" ]; then
    echo "ERROR: OVH_HOST not configured in .env"
    exit 1
fi

if [ -z "$OVH_USER" ] || [ "$OVH_USER" = "your-username" ]; then
    echo "ERROR: OVH_USER not configured in .env"
    exit 1
fi

if [ -z "$OVH_PATH" ]; then
    echo "ERROR: OVH_PATH not configured in .env"
    exit 1
fi

# Check data files exist
if [ ! -f "data/stats.json" ]; then
    echo "ERROR: data/ not found. Run generate_webapp.py first:"
    echo "  python generate_webapp.py"
    exit 1
fi

echo "=== Amazon Review Analyzer — Deploy to OVH ==="
echo ""
echo "  Host: ${OVH_HOST}"
echo "  User: ${OVH_USER}"
echo "  Path: ${OVH_PATH}"
echo ""
echo "Files to upload:"
echo "  index.html"
echo "  data/stats.json"
echo "  data/clusters.json"
echo "  data/clusters_local.json"
echo "  data/products.json"
echo "  data/reviews_sample.json"
echo ""

# Upload via SFTP
echo "Uploading via SFTP..."
sftp ${OVH_USER}@${OVH_HOST} << EOF
mkdir ${OVH_PATH}
mkdir ${OVH_PATH}/data
put index.html ${OVH_PATH}/index.html
put data/stats.json ${OVH_PATH}/data/stats.json
put data/clusters.json ${OVH_PATH}/data/clusters.json
put data/clusters_local.json ${OVH_PATH}/data/clusters_local.json
put data/products.json ${OVH_PATH}/data/products.json
put data/reviews_sample.json ${OVH_PATH}/data/reviews_sample.json
quit
EOF

echo ""
echo "Done! Your app should be live."

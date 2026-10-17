#!/bin/bash
# ==============================================================================
# Value Physics Research Repository — Automated Sync & Site Build Script
# Alethekanon Research Institute — Division 2
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================================="
echo " Starting Value Physics HTML Site Generation & Sync..."
echo " Time: $(date)"
echo "=========================================================="

# 1. Verify Python 3
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required to build the Value Physics site."
    exit 1
fi

# 2. Run data parsing and site generation (supports raw downloads or JSON fallback)
python3 build_value_physics_site.py

# 3. Verify generated artifacts
echo "Checking generated files..."
for f in index.html papers.html data.html changelog.html updates.html workflow.html; do
    if [ -f "$f" ]; then
        SIZE=$(stat -c%s "$f" 2>/dev/null || stat -f%z "$f" 2>/dev/null || echo "OK")
        echo " [OK] $f ($SIZE bytes)"
    else
        echo " [FAIL] Missing $f"
        exit 1
    fi
done

echo "=========================================================="
echo " Site build successful! All pages generated in HTML."
echo " To preview locally:"
echo "   python3 -m http.server 8000"
echo "   Visit: http://localhost:8000"
echo "=========================================================="

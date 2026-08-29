#!/usr/bin/env bash
set -uo pipefail
V=/opt/data/raf-venv
uv venv "$V" --quiet 2>&1 | tail -1
echo "=== install hccinfhir (Apache-2.0 RAF engine, V24+V28) ==="
uv pip install --python "$V/bin/python" hccinfhir 2>&1 | tail -5
echo "=== verify import + bundled model files ==="
"$V/bin/python" -c "
import hccinfhir, os, pkgutil
print('hccinfhir ok', getattr(hccinfhir,'__version__','?'))
p = os.path.dirname(hccinfhir.__file__)
import glob
files = glob.glob(p+'/data/*.csv') + glob.glob(p+'/**/*.csv', recursive=True)
print('bundled data files:', len(files))
for f in sorted(files)[:12]:
    print('  ', os.path.basename(f))
"

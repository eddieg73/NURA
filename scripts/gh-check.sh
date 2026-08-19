#!/bin/bash
chmod +x /opt/data/bin/gh-cli
/opt/data/bin/gh-cli --version 2>&1 | head -1
/opt/data/bin/gh-cli repo view Eddieg73/nura_medical 2>&1 | head -3

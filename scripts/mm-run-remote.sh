#!/bin/bash
# Run broadcast ON the Clinic with the token passed in
TOK="$1"
sed -i "s|^TOK=.*|TOK=\"$TOK\"|" /tmp/mm-broadcast.sh 2>/dev/null
bash /tmp/mm-broadcast.sh 2>&1 | head -5

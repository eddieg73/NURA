#!/bin/bash
# Sealed email app-password provider (chmod 700, never echoed)
grep -E '^GOOGLE_OAUTH_PASSWORD=' /opt/data/profiles/nura/.env | head -1 | cut -d= -f2- | tr -d '"' | tr -d "'"

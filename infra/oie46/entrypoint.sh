#!/bin/sh
set -e
CONF=/opt/oie/conf/mirth.properties

if [ -n "${DATABASE+x}" ]; then
  sed -i "s|^database\\s*=.*$|database = ${DATABASE}|" "$CONF"
fi
if [ -n "${DATABASE_URL+x}" ]; then
  sed -i "s|^database\\.url\\s*=.*$|database.url = ${DATABASE_URL}|" "$CONF"
fi
if [ -n "${DATABASE_USERNAME+x}" ]; then
  sed -i "s|^database\\.username\\s*=.*$|database.username = ${DATABASE_USERNAME}|" "$CONF"
fi
if [ -n "${DATABASE_PASSWORD+x}" ]; then
  sed -i "s|^database\\.password\\s*=.*$|database.password = ${DATABASE_PASSWORD}|" "$CONF"
fi

exec ./oieserver

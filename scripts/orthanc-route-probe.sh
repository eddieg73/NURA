#!/bin/bash
# Orthanc plugin route introspection — run from the nginx container (has curl)
set -e
PW=$(docker exec radris-stack-orthanc-1 printenv ORTHANC_PASSWORD)
echo "--- plugins ---"
docker exec radris-stack-nginx-1 sh -c "curl -s -m 8 -u orthanc:$PW http://orthanc:8042/plugins" | head -c 700
echo
echo "--- dicom-web routes ---"
docker exec radris-stack-nginx-1 sh -c "curl -s -m 8 -u orthanc:$PW http://orthanc:8042/plugins/dicom-web/routes" | head -c 700
echo
echo "--- web-viewer routes ---"
docker exec radris-stack-nginx-1 sh -c "curl -s -m 8 -u orthanc:$PW http://orthanc:8042/plugins/web-viewer/routes" | head -c 700
echo
echo "--- direct QIDO /dicom-web ---"
docker exec radris-stack-nginx-1 sh -c "curl -s -m 8 -o /dev/null -w '%{http_code}' -u orthanc:$PW 'http://orthanc:8042/dicom-web/studies?limit=1'"
echo
echo "--- direct QIDO /web-viewer/dicom-web ---"
docker exec radris-stack-nginx-1 sh -c "curl -s -m 8 -o /dev/null -w '%{http_code}' -u orthanc:$PW 'http://orthanc:8042/web-viewer/dicom-web/studies?limit=1'"
echo

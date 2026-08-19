#!/bin/bash
# Build the hybrid Orthanc plugin dir: DICOMweb (legacy layer) + PostgreSQL (new image)
set -e
P=/docker/radris-stack/plugins
rm -rf "$P" /tmp/plugins-new
mkdir -p "$P" /tmp/plugins-new
# current image's plugins (explorer2, gdcm, postgresql-index, postgresql-storage)
docker cp radris-stack-orthanc-1:/usr/share/orthanc/plugins/. /tmp/plugins-new/
# legacy layer's DICOMweb plugin
docker cp orthanc-pacs:/usr/share/orthanc/plugins/libOrthancDicomWeb.so /tmp/plugins-new/
cp -f /tmp/plugins-new/*.so "$P"/
ls -la "$P/"

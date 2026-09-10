#!/usr/bin/env bash
# Gather Orthanc + OpenEMR config on clinic (read-only)
CFG=/opt/data/profiles/nura/home/.ssh/config
OU=$(grep '^ORTHANC_USER=' /opt/data/profiles/nura/.env | cut -d= -f2 | tr -d '"')
OP=$(grep '^ORTHANC_PASS=' /opt/data/profiles/nura/.env | cut -d= -f2 | tr -d '"')
echo "=== Orthanc (authed) ==="
ssh -F "$CFG" -o ConnectTimeout=20 clinic "
  echo -n '  system: '; curl -s --max-time 8 -u '$OU:$OP' http://localhost:8042/system 2>/dev/null | head -c 240; echo
  echo -n '  modalities: '; curl -s --max-time 8 -u '$OU:$OP' http://localhost:8042/modalities 2>/dev/null | head -c 160; echo
  echo -n '  studies: '; curl -s --max-time 8 -u '$OU:$OP' http://localhost:8042/studies 2>/dev/null | head -c 120; echo
  echo -n '  DICOMweb QIDO: '; curl -s -o /dev/null -w '%{http_code}' --max-time 8 -u '$OU:$OP' 'http://localhost:8042/dicom-web/studies' 2>/dev/null; echo
  echo -n '  env AET/PORT: '; docker inspect radris-stack-orthanc-1 --format '{{range .Config.Env}}{{println .}}{{end}}' 2>/dev/null | grep -iE 'AET|PORT|DICOM|VERBOSE' | tr '\n' ' ' | head -c 200; echo
" 2>&1 | head -22
echo ""
echo "=== OpenEMR version ==="
ssh -F "$CFG" -o ConnectTimeout=15 clinic "docker exec openemr-zklo-openemr-1 sh -c 'grep -E \"v_major|v_minor|v_patch|v_tag\" /var/www/localhost/htdocs/openemr/version.php' 2>/dev/null | tail -5" 2>&1 | head -8

#!/usr/bin/env python3
"""NURA Orthanc PACS MCP — the wrap of the Orthanc REST API (the API v30).
The pattern: the Perfex MCP's the (the T() + the route_tool + the api_request).
The read-first tools + the modality management. The auth: the nuraadmin.
"""
import os, sys, json, base64, urllib.request

ORTHANC_URL = os.environ.get("ORTHANC_URL", "http://127.0.0.1:8042")
ORTHANC_USER = os.environ.get("ORTHANC_USER", "nuraadmin")
ORTHANC_PASS = os.environ.get("ORTHANC_PASS", "")

def api(path, method="GET", body=None):
    req = urllib.request.Request(f"{ORTHANC_URL}{path}", method=method)
    if ORTHANC_USER:
        auth = base64.b64encode(f"{ORTHANC_USER}:{ORTHANC_PASS}".encode()).decode()
        req.add_header("Authorization", f"Basic {auth}")
    if body is not None:
        req.add_header("Content-Type", "application/json")
        data = json.dumps(body).encode()
    else:
        data = None
    try:
        with urllib.request.urlopen(req, data=data, timeout=30) as r:
            return json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        return {"_error": f"HTTP {e.code}", "_body": e.read().decode()[:200]}
    except Exception as e:
        return {"_error": str(e)[:150]}

# the tool definitions (the name, the description, the path builder)
TOOLS = [
    ("orthanc_system", "The Orthanc system info (the version, the capabilities, the plugins)", lambda a: ("/system", "GET", None)),
    ("orthanc_statistics", "The instance/series/study/patient counts", lambda a: ("/statistics", "GET", None)),
    ("orthanc_patients", "List the patients", lambda a: ("/patients", "GET", None)),
    ("orthanc_patient_studies", "The patient's studies", lambda a: (f"/patients/{a['patient_id']}/studies", "GET", None)),
    ("orthanc_studies", "List the studies (the optional limit/offset)", lambda a: (f"/studies?limit={a.get('limit', 20)}", "GET", None)),
    ("orthanc_study_info", "The study's the metadata", lambda a: (f"/studies/{a['study_id']}", "GET", None)),
    ("orthanc_study_series", "The study's series list", lambda a: (f"/studies/{a['study_id']}/series", "GET", None)),
    ("orthanc_series_instances", "The series' instances", lambda a: (f"/series/{a['series_id']}/instances", "GET", None)),
    ("orthanc_instance_tags", "The instance's DICOM tags", lambda a: (f"/instances/{a['instance_id']}/tags", "GET", None)),
    ("orthanc_instance_simplified", "The instance's simplified tags", lambda a: (f"/instances/{a['instance_id']}/simplified-tags", "GET", None)),
    ("orthanc_instance_file", "The instance's DICOM file (the base64)", lambda a: (f"/instances/{a['instance_id']}/file", "GET", None)),
    ("orthanc_modalities_list", "List the DICOM modalities (the AEs)", lambda a: ("/modalities", "GET", None)),
    ("orthanc_modality_add", "Add a DICOM modality (the AE title, the host, the port)", lambda a: (f"/modalities/{a['ae']}", "PUT", {"AET": a['ae'], "Host": a.get('host', ''), "Port": int(a.get('port', 104))})),
    ("orthanc_modality_delete", "Delete a DICOM modality", lambda a: (f"/modalities/{a['ae']}", "DELETE", None)),
    ("orthanc_peers", "List the DICOM peers", lambda a: ("/peers", "GET", None)),
    ("orthanc_query_study", "The C-FIND the a modality for the studies (the patient ID etc.)", lambda a: ("/modalities/{mod}/query".replace("{mod}", a['modality']), "POST", {"Level": "Study", "Query": a.get('query', {})})),
    ("orthanc_dicom_echo", "The C-ECHO a modality", lambda a: (f"/modalities/{a['modality']}/echo", "POST", None)),
    ("orthanc_study_archive", "Download the study as the DICOMDIR zip (the base64)", lambda a: (f"/studies/{a['study_id']}/archive", "GET", None)),
    ("orthanc_jobs", "List the running jobs", lambda a: ("/jobs", "GET", None)),
]

def handle(name, args):
    for t in TOOLS:
        if t[0] == name:
            path, method, body = t[2](args)
            return api(path, method, body)
    return {"_error": f"unknown tool {name}"}

def list_tools():
    return [{"name": t[0], "description": t[1]} for t in TOOLS]

if __name__ == "__main__":
    # the CLI mode:  python orthanc-mcp.py <tool> [json args]
    if len(sys.argv) < 2:
        print(json.dumps(list_tools(), indent=2))
    else:
        name = sys.argv[1]
        args = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
        print(json.dumps(handle(name, args), indent=2, default=str))

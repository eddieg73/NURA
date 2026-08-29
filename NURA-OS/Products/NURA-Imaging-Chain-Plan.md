# THE NURA IMAGING-CHAIN MASTER-PLAN (2026-08-10!)

## The vision: ONE imaging-workflow across the EMR ↔ RIS ↔ PACS ↔ Viewer!
```
OpenEMR (the EMR — the orders + the results!)
   │  ORM (the imaging-order HL7!)
   ▼
MIRTH (the hub — the HL7-routing!)
   │
   ├──► ThaiRIS (the RIS — the scheduling + the worklist!)
   │       │  ORU (the result-HL7!)
   │       ▼
   │   MIRTH ──► OpenEMR (the result-document!)
   │
   └──► Orthanc (the PACS — the DICOM-storage!)
           │  DICOMweb
           ▼
       OHIF-Viewer (the viewing!)
```

## The wiring-status (08-10!)
- ✅ OpenEMR: the 20-tool-MCP + the FHIR-lane — the EMR-side-ready!
- ✅ Mirth: the API-LIVE (the 4.5.2, the REST-8444!) — the channels-EMPTY (the building!)
- ✅ Orthanc: the modality-added (["mirth"] ✓!) — the PACS-side-ready!
- ✅ ThaiRIS: the web-200 (the :32790!) + the MySQL-lane (the creds-hunt!)
- ⏳ OHIF: the container-up (:32791!) — the Orthanc-connect-config!

## The channel-build (the Mirth-side!)
1. **DICOM-to-Orthanc** (the C-STORE-route — the in-progress, the transformer-fix!):
   - Source: the DICOM-Listener (AET-MIRTH · :6661!) → Destination: the Orthanc-C-STORE (AET-ORTHANC · :4242!)
2. **ORM-to-ThaiRIS** (the order-route!):
   - Source: the OpenEMR-HL7 (the ORM^O01!) → Destination: the ThaiRIS-HL7!
3. **ORU-to-OpenEMR** (the result-route!):
   - Source: the ThaiRIS-HL7 (the ORU^R01!) → Destination: the OpenEMR-HL7/FHIR!
4. **The OHIF-viewer**: the config → the Orthanc-data-source (the DICOMweb-lane!)

## The ThaiRIS-side (the RIS-lane!)
- The ThaiRIS-API: the thairisfree-source-study (the REST-endpoints-hunt!)
- The MySQL-lane: the creds-sealed → the patient/order-tables (the ETL-option!)
- The RIS-worklist: the scheduled-studies ↔ the OpenEMR-orders (the Mirth-mediated!)

## The verification (the end-to-end!)
1. The OpenEMR-order → the Mirth-ORM → the ThaiRIS-worklist ✓
2. The ThaiRIS-complete → the ORU → the Mirth → the OpenEMR-result ✓
3. The study-stored → the Orthanc (the C-STORE!) → the OHIF-view ✓
4. The audit: every-step-logged (the Mirth-dashboard + the OpenEMR-audit!)

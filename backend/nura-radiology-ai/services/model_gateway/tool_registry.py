"""Tool allowlist / denylist (spec). The reasoning model may call ONLY allowed tools that
produce context or drafts — never destructive or authority-granting tools."""

TOOL_ALLOWLIST = [
    # context / retrieval (read-only clinical + evidence)
    "get_patient_context",
    "get_prior_imaging_report",
    "get_structured_imaging_findings",
    "search_pubmed",
    "get_fda_drug_label",
    "get_lab_trends",
    "get_guideline_evidence",
    "get_model_validation",
    # draft / decision outputs (never finalize)
    "create_draft_report",
    "create_ranked_differential",
    "request_provider_review",
    # storage (read + presign only) via gateway
    "storage_get_metadata", "storage_request_read_url", "storage_verify_checksum",
]

TOOL_DENYLIST = [
    "delete_study", "write_final_diagnosis", "send_patient_result", "prescribe_medication",
    "execute_shell", "raw_database_query", "unrestricted_email_send", "finalize_radiology_report",
    "delete_all_objects", "delete_bucket", "list_all_buckets", "storage_unsafe_raw",
]

def is_tool_allowed(name: str) -> bool:
    if name in TOOL_DENYLIST:
        return False
    return name in TOOL_ALLOWLIST

def assert_tool_allowed(name: str) -> None:
    if not is_tool_allowed(name):
        raise PermissionError(f"tool '{name}' is not on the model-gateway allowlist")

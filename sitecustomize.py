"""
Compatibility shim for environments where google.cloud.compute_v1 lacks a 'types' attribute.
This helps tests that reference compute_v1.types by aliasing it to the module itself.
The module is auto-imported by Python at startup if present on sys.path.
"""

# Keep this extremely defensive; it should never raise on import.
try:
    from google.cloud import compute_v1 as _compute_v1
    # Some versions of google-cloud-compute don't expose a 'types' attribute.
    if not hasattr(_compute_v1, "types"):
        # Alias 'types' to the module itself so attribute access works in tests.
        _compute_v1.types = _compute_v1  # type: ignore[attr-defined]
except Exception:
    # Silently ignore any issues; this shim is best-effort only.
    pass

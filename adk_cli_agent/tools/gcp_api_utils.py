"""Shared utilities for GCP API and gcloud CLI operations."""

# - Checking gcloud CLI availability
# - Running gcloud commands
# - Handling Google Cloud credentials
# - Any other shared logic between project management functions

try:
    import google.auth
    HAS_GCP_AUTH = True
except ImportError:
    HAS_GCP_AUTH = False

def get_gcp_credentials():
    """Get Google Cloud credentials from the default location.
    
    Returns:
        google.auth.credentials.Credentials: The credentials object
        
    Raises:
        ImportError: If Google Auth libraries are not available
        Exception: If credentials could not be obtained
    """
    if not HAS_GCP_AUTH:
        raise ImportError("Google Cloud Authentication libraries not available. Install with 'pip install google-auth'")
        
    try:
        credentials, _ = google.auth.default()
        return credentials
    except Exception as e:
        raise Exception(f"Failed to obtain Google Cloud credentials: {e}")

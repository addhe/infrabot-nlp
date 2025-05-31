"""Authentication and organization-related utilities for GCP tools."""
import os
import json
from typing import Optional, Tuple, Dict, Any
import google.auth
from google.oauth2 import service_account
from google.cloud import resourcemanager_v3
from my_cli_agent.tools.gcp.base.exceptions import GCPToolsError

def get_credentials_info() -> Dict[str, Any]:
    """Get information about the current credentials being used.
    
    Returns:
        Dict containing:
            - type: "service_account" or "user_account"
            - email: The account email
            - quota_project: The quota project ID (for user credentials)
    """
    try:
        # First try service account from environment variable
        if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
            with open(os.getenv('GOOGLE_APPLICATION_CREDENTIALS')) as f:
                sa_info = json.load(f)
                return {
                    "type": "service_account",
                    "email": sa_info.get("client_email"),
                    "quota_project": None
                }
        
        # Then try ADC location
        adc_path = os.path.expanduser("~/.config/gcloud/application_default_credentials.json")
        if os.path.exists(adc_path):
            with open(adc_path) as f:
                adc_info = json.load(f)
                return {
                    "type": "user_account",
                    "email": adc_info.get("client_id"),  # This is actually the OAuth client ID
                    "quota_project": adc_info.get("quota_project_id")
                }
                
        raise GCPToolsError("No credentials found")
        
    except Exception as e:
        raise GCPToolsError(f"Error reading credentials: {str(e)}")

def get_organization_details() -> Tuple[Optional[str], Optional[str]]:
    """Get organization ID and name from the current credentials.
    
    Returns:
        Tuple[Optional[str], Optional[str]]: A tuple containing:
            - organization_id: The full organization ID (e.g., 'organizations/123456')
            - organization_name: The display name of the organization
            
        Returns (None, None) if no organization is found or if credentials don't have access.
    """
    try:
        # First try to get from environment variable
        org_id = os.getenv('GCP_ORGANIZATION_ID')
        if org_id:
            if not org_id.startswith('organizations/'):
                org_id = f'organizations/{org_id}'
            return org_id, None
            
        # Try using gcloud for user credentials
        try:
            import subprocess
            result = subprocess.run(
                ['gcloud', 'organizations', 'list', '--format=json'],
                capture_output=True,
                text=True,
                check=True
            )
            if result.stdout:
                orgs = json.loads(result.stdout)
                if orgs:
                    return f"organizations/{orgs[0]['name']}", orgs[0].get('displayName')
        except Exception as e:
            print(f"Could not get organization from gcloud: {e}")
            
        # Try using API client as fallback
        credentials, _ = google.auth.default()
        client = resourcemanager_v3.OrganizationsClient(credentials=credentials)
        
        try:
            orgs = list(client.search_organizations())
            if orgs:
                return orgs[0].name, orgs[0].display_name
        except Exception as e:
            print(f"Could not list organizations via API: {e}")
            
        return None, None
            
    except Exception as e:
        print(f"Warning: Error getting organization details: {e}")
        return None, None

def validate_credentials(require_org: bool = True) -> bool:
    """Validate GCP credentials.
    
    Args:
        require_org (bool): Whether to require organization access
        
    Returns:
        bool: True if credentials are valid
    """
    try:
        credentials, project = google.auth.default()
        print(f"Using credentials type: {type(credentials).__name__}")
        
        # Check if we have user credentials
        is_user_credentials = 'user' in str(type(credentials).__name__).lower()
        
        if require_org and not is_user_credentials:
            # Only check org access for service accounts
            org_id, _ = get_organization_details()
            if not org_id:
                print("No organization access found")
                if require_org:
                    print("Service accounts require organization access")
                    return False
                
        # For user credentials, try to verify access using gcloud
        if is_user_credentials:
            try:
                import subprocess
                result = subprocess.run(
                    ['gcloud', 'auth', 'print-access-token'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                if result.stdout.strip():
                    print("Valid user credentials found")
                    return True
            except Exception as e:
                print(f"Failed to verify gcloud credentials: {e}")
                print("Please run 'gcloud auth login' to authenticate")
                return False
                
        return True
        
    except Exception as e:
        print(f"Failed to validate credentials: {e}")
        return False

def get_project_parent(require_org: bool = True) -> Optional[str]:
    """Get the parent resource (organization) for new projects.
    
    Args:
        require_org: If True (default), require organization access. If False,
                    organization is optional when using ADC.
    
    Returns:
        Optional[str]: The parent resource string (e.g., 'organizations/123456') 
                      or None if no valid parent is found.
    """
    try:
        creds_info = get_credentials_info()
        org_id, _ = get_organization_details()

        if org_id:
            return org_id
        elif not require_org and creds_info["type"] == "user_account":
            return None
        else:
            return None
    except Exception as e:
        print(f"Warning: Error getting project parent: {str(e)}")
        return None

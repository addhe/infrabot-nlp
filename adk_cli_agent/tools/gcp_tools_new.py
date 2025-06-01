"""Google Cloud Platform (GCP) tools for ADK CLI Agent.

This module provides a thin wrapper around the modular GCP tools implementation,
adapting the lower-level API to work with ADK's function declarations.
"""

import os
import json
from typing import Dict, Any, Optional

from my_cli_agent.tools.gcp.management import (
    ProjectManager, 
    get_project_manager
)
from my_cli_agent.tools.gcp.base.exceptions import GCPToolsError

# Check if GCP tools are available
try:
    import google.auth
    from google.cloud import resourcemanager_v3
    HAS_GCP_TOOLS_FLAG = True
except ImportError:
    HAS_GCP_TOOLS_FLAG = False


def list_gcp_projects(env: str) -> Dict[str, Any]:
    """Lists Google Cloud Platform (GCP) projects.
    
    If 'env' is 'all', it lists all accessible projects.
    Otherwise, it attempts to filter projects for a specified environment (dev/stg/prod)
    based on project ID or name.
    
    Args:
        env (str): The environment to list projects for (dev/stg/prod/all).
        
    Returns:
        dict: Contains status and the list of projects as a report, or an error message.
    """
    print(f"--- Tool: list_gcp_projects called with env={env} ---")
    
    # Normalize env parameter
    env = env.lower() if env else "all"
    
    try:
        # Get project manager from the new modular implementation
        manager = get_project_manager()
        # Get all projects first
        all_projects = manager.list_projects()
        
        # Then filter based on environment if needed
        if env != "all":
            projects = [
                p for p in all_projects 
                if env in p.project_id.lower() or 
                   (p.name and env in p.name.lower())
            ]
        else:
            projects = all_projects
        
        if not projects:
            return {
                "status": "success",
                "report": f"Tidak ada proyek ditemukan untuk environment: {env}"
            }
        
        # Initialize lists for different project states
        active_project_lines = []
        pending_delete_lines = []
        
        # Count projects by status
        active_count = 0
        pending_count = 0
        
        # Format projects with enhanced information
        for project in projects:
            # Format status info and count
            status_info = ""
            state_indicator = "🟢"  # Default active
            
            if project.status == "DELETE_REQUESTED":
                status_info = "(MENUNGGU PENGHAPUSAN - Akan dihapus permanen dalam 30 hari)"
                state_indicator = "🔴"
                pending_count += 1
            elif project.status == "DELETE_IN_PROGRESS":
                status_info = "(SEDANG DIHAPUS)"
                state_indicator = "🔴"
                pending_count += 1
            elif project.status == "INACTIVE":
                status_info = "(TIDAK AKTIF)"
                state_indicator = "⚫"
                active_count += 1  # Count as active but mark as inactive
            elif project.status == "ACTIVE":
                active_count += 1
            else:
                status_info = f"(TIDAK DIKETAHUI - {project.status})"
                state_indicator = "⚪"
                active_count += 1  # Count unknown status as active
            
            # Format project line
            project_line = f"{state_indicator} {project.name} ({project.project_id})"
            if status_info:
                project_line += f" {status_info}"
                
            # Add to appropriate list
            if project.status in ["DELETE_REQUESTED", "DELETE_IN_PROGRESS"]:
                pending_delete_lines.append(project_line)
            else:
                active_project_lines.append(project_line)
        
        # Prepare report sections
        report_sections = []
        
        # Header with counts
        total_projects = active_count + pending_count
        if total_projects == 0:
            status_counts = "Tidak ada proyek ditemukan"
        else:
            status_counts = f"Ditemukan {total_projects} proyek total"
            if pending_count > 0:
                status_counts += f" ({active_count} aktif, {pending_count} menunggu penghapusan)"
        report_sections.append(status_counts)
        
        # Active projects
        if active_project_lines:
            report_sections.append("\nProyek Aktif:")
            report_sections.extend(active_project_lines)
            
        # Pending deletion
        if pending_delete_lines:
            report_sections.append("\nProyek Menunggu Penghapusan:")
            report_sections.extend(pending_delete_lines)
            
        # Status legend
        report_sections.extend([
            "",
            "Legenda Status:",
            "🟢 AKTIF",
            "⚫ TIDAK AKTIF",
            "🔴 MENGHAPUS",
            "⚪ TIDAK DIKETAHUI"
        ])
        
        return {
            "status": "success",
            "report": "\n".join(report_sections)
        }
        
    except GCPToolsError as e:
        return {
            "status": "error",
            "error_message": f"Terjadi kesalahan: {str(e)}"
        }
    except Exception as e:
        error_msg = f"Terjadi kesalahan yang tidak terduga: {str(e)}"
        print(f"ERROR: {error_msg}")
        return {
            "status": "error",
            "error_message": error_msg
        }


def create_gcp_project(project_id: str, project_name: str) -> Dict[str, Any]:
    """Creates a new Google Cloud Platform (GCP) project.
    
    Args:
        project_id (str): The ID for the new project (must be globally unique)
        project_name (str): The display name for the new project. 
            If empty, project_id will be used as the name.
        
    Returns:
        dict: Contains status and the result or error message.
    """
    print(f"--- Tool: create_gcp_project called with project_id={project_id}, "
          f"project_name={project_name} ---")
          
    try:
        # Basic validation
        if not project_id:
            return {
                "status": "error",
                "error_message": "ID Proyek harus diisi. Contoh format: awan-testing-001"
            }
            
        if not project_id.islower() or not project_id.replace('-', '').isalnum():
            return {
                "status": "error",
                "error_message": "ID Proyek hanya boleh menggunakan huruf kecil, angka, dan tanda hubung (-)"
            }
            
        # Normalize project name - if empty or None, use formatted project_id
        effective_name = (project_name if project_name and project_name.strip() 
                        else project_id.replace('-', ' ').title())
        
        # Get project manager and create project
        manager = get_project_manager()
        project = manager.create_project(
            project_id=project_id,
            name=effective_name
        )
        
        return {
            "status": "success",
            "report": (f"Proyek baru telah dibuat:\n"
                      f"  Nama: {project.name}\n"
                      f"  ID: {project.project_id}\n"
                      f"  Status: {project.status}")
        }
        
    except GCPToolsError as e:
        if "ALREADY_EXISTS" in str(e):
            return {
                "status": "error",
                "error_message": f"ID Proyek '{project_id}' sudah digunakan. Silakan gunakan ID proyek yang lain."
            }
        return {
            "status": "error",
            "error_message": f"Terjadi kesalahan: {str(e)}"
        }
    except Exception as e:
        error_msg = f"Gagal membuat proyek GCP '{project_id}': {str(e)}"
        print(f"ERROR: {error_msg}")
        return {
            "status": "error",
            "error_message": error_msg
        }


def delete_gcp_project(project_id: str) -> Dict[str, Any]:
    """Deletes a Google Cloud Platform (GCP) project.
    
    Args:
        project_id (str): The ID of the project to delete.
        
    Returns:
        dict: Contains status and the result or error message.
    """
    print(f"--- Tool: delete_gcp_project called with project_id={project_id} ---")
    
    try:
        manager = get_project_manager()
        
        # First list the project to check if it exists and get its details
        try:
            # Get all projects first
            all_projects = manager.list_projects()  # Don't pass env parameter
            # Then filter for the specific project
            project = next((p for p in all_projects if p.project_id == project_id), None)
            
            if not project:
                return {
                    "status": "error",
                    "error_message": f"Proyek '{project_id}' tidak ditemukan"
                }
                
            # Check project state
            if project.status == "DELETE_REQUESTED":
                return {
                    "status": "error",
                    "error_message": f"Proyek '{project_id}' sudah dalam antrian penghapusan"
                }
            elif project.status == "DELETE_IN_PROGRESS":
                return {
                    "status": "error",
                    "error_message": f"Proyek '{project_id}' sedang dalam proses penghapusan"
                }
            
            # Confirm details before deletion
            confirm_msg = (
                f"\nAnda akan menghapus proyek berikut:\n"
                f"  Nama: {project.name}\n"
                f"  ID: {project.project_id}\n"
                f"  Status: {project.status}\n\n"
                f"Anda yakin? Tindakan ini tidak dapat dibatalkan. [y/N]: "
            )
            
            if input(confirm_msg).lower() not in ['y', 'yes']:
                return {
                    "status": "success",
                    "report": "Penghapusan proyek dibatalkan oleh pengguna"
                }
            
            # Proceed with deletion
            manager.delete_project(project_id)
            
            return {
                "status": "success",
                "report": f"Penghapusan proyek '{project.name}' ({project_id}) telah dimulai. "
                         "Proyek akan dihapus secara permanen setelah 30 hari."
            }
            
        except GCPToolsError as list_error:
            return {
                "status": "error",
                "error_message": f"Gagal mendapatkan informasi proyek: {str(list_error)}"
            }
            
    except GCPToolsError as e:
        return {
            "status": "error",
            "error_message": f"Terjadi kesalahan: {str(e)}"
        }
    except Exception as e:
        error_msg = f"Gagal menghapus proyek GCP '{project_id}': {str(e)}"
        print(f"ERROR: {error_msg}")
        return {
            "status": "error",
            "error_message": error_msg
        }

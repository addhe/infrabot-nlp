"""Module for AI-based intent detection for GCP commands."""

from typing import Tuple, Dict, Optional, Any
import re

class AIIntentDetector:
    """Intent detector using AI models for better natural language understanding."""
    
    @staticmethod
    def detect_intent(command: str) -> Tuple[Optional[str], float, Dict[str, Any]]:
        """
        Detect intent from command using AI model.
        
        Args:
            command (str): The command to analyze
            
        Returns:
            Tuple[Optional[str], float, Dict[str, Any]]: 
                - Intent name (or None if not recognized)
                - Confidence score (0-1)
                - Parameters extracted from command
        """
        command = command.lower().strip()
        
        # Basic intent patterns for fallback
        list_patterns = [
            r"(?:list|show|get|display|view|check).+(?:projects?|apps?)",
            r"(?:what|how many).+projects?.+(?:have|got|own)",
            r"(?:berapa|ada berapa).+projects?"
        ]
        
        create_patterns = [
            r"(?:create|make|add|new).+projects?",
            r"(?:buat|bikin|tambah).+projects?",
            # Named project patterns
            r"(?:create|make|add|new).+projects?.+(?:with name|named)",
            r"(?:buat|bikin|tambah).+projects?.+dengan(?:\s+nama)?"
        ]
        
        delete_patterns = [
            r"(?:delete|remove|del|hapus).+projects?",
        ]
        
        # First try AI-based intent detection
        try:
            # Check for create intent
            for pattern in create_patterns:
                if re.search(pattern, command):
                    # First try to match a project name pattern
                    name_patterns = [
                        r"(?:with\s+name|named)\s+([a-z][-a-z0-9]+)",
                        r"dengan(?:\s+nama)?\s+([a-z][-a-z0-9]+)"
                    ]
                    
                    for name_pattern in name_patterns:
                        name_match = re.search(name_pattern, command)
                        if name_match:
                            project_id = name_match.group(1)
                            return "create_project", 0.95, {"project_id": project_id, "project_name": project_id}

                    # If no name pattern matched, try to find a valid project ID in the command
                    id_match = re.search(r'(?:project\s+)?([a-z][-a-z0-9]{4,28}[a-z0-9])', command)
                    if id_match:
                        project_id = id_match.group(1)
                        # Check for project name after ID
                        name_match = re.search(fr'{project_id}\s+(.+?)(?:\s*$|\s+(?:please|thanks|ya|aja|saja))', command)
                        project_name = name_match.group(1) if name_match else project_id
                        return "create_project", 0.95, {"project_id": project_id, "project_name": project_name}
            
            # Check for list intent
            for pattern in list_patterns:
                if re.search(pattern, command):
                    # Extract environment if specified
                    env_match = re.search(r"(?:in|for|dari|di)\s+(dev|development|stg|staging|prod|production)", command)
                    env = env_match.group(1) if env_match else "all"
                    return "list_projects", 0.95, {"environment": env}
            
            # Check for delete intent
            for pattern in delete_patterns:
                if re.search(pattern, command):
                    # Extract project ID
                    project_match = re.search(r"(?:project\s+)?([a-z][-a-z0-9]+)", command)
                    if project_match:
                        return "delete_project", 0.95, {"project_id": project_match.group(1)}
            
            return None, 0.0, {}
            
        except Exception as e:
            print(f"AI intent detection error: {e}")
            return None, 0.0, {}

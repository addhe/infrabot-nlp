"""Intent detection for GCP tools commands using fuzzy matching and pattern recognition."""
from typing import Dict, List, Tuple, Optional
from difflib import SequenceMatcher
import re

class IntentDetector:
    """Detects command intents using fuzzy matching and pattern recognition."""

    # Intent patterns for different languages
    INTENT_PATTERNS = {
        "list_projects": {
            "en": [
                r"list.*projects?",
                r"show.*projects?",
                r"get.*projects?",
                r"display.*projects?",
                r"what.*projects?.*(?:have|own|available)",
                r"how.*many.*projects?"
            ],
            "id": [
                r"tampilkan.*projects?",
                r"lihat.*projects?",
                r"tunjukkan.*projects?",
                r"daftar.*projects?",
                r"list.*projects?",
                r"berapa.*projects?",
                r"ada.*berapa.*projects?",
                r"cek.*projects?",
                r"project.*apa.*(?:saja|aja).*(?:yang|yg).*(?:ada|dimiliki|punya)",
                r"tolong.*(?:tampilkan|lihat|tunjukkan).*projects?",
                # New patterns for Indonesian
                r"(?:project|projects?).*(?:yang|yg).*(?:saya|aku|kita).*(?:miliki|punya)",
                r"(?:project|projects?).*(?:yang|yg).*(?:ada|tersedia|dimiliki)",
                r"(?:lihat|tampilkan|tunjukkan).*(?:project|projects?).*(?:saya|aku|kita)"
            ]
        },
        "create_project": {
            "en": [
                r"create.*(?:new\s+)?projects?",
                r"new.*projects?",
                r"make.*projects?",
                r"add.*projects?",
                r"create.*projects?.*(?:with|named)",
                r"create.*multiple.*projects?",
                r"create.*projects?.*(and|,)"
            ],
            "id": [
                r"buat.*projects?.*(?:dengan nama.*|$)",
                r"bikin.*projects?.*(?:dengan nama.*|$)",
                r"tambah.*projects?.*(?:dengan nama.*|$)",
                r"create.*projects?.*(?:dengan nama.*|$)",
                r"buat.*baru.*(?:dengan nama.*|$)", 
                r"bikin.*baru.*(?:dengan nama.*|$)",
                r"project.*baru.*(?:dengan nama.*|$)",
                r"buat.*projects?.*(dan|,)",
                r"bikin.*projects?.*(dan|,)",
                r"tambah.*projects?.*(dan|,)"
            ]
        },
        "delete_project": {
            "en": [
                r"delete.*projects?",
                r"remove.*projects?",
                r"drop.*projects?",
                # Bulk deletion patterns
                r"delete.*(multiple|several|many).*projects?",
                r"delete.*projects?.*(and|,)",
                r"delete.*all.*projects?.*(?:in|from)",
                r"bulk.*delete.*projects?"
            ],
            "id": [
                r"hapus.*projects?",
                r"delete.*projects?",
                r"buang.*projects?",
                r"hilangkan.*projects?",
                # Bulk deletion patterns in Indonesian
                r"hapus.*(beberapa|banyak|semua).*projects?",
                r"hapus.*projects?.*(dan|,)",
                r"hapus.*projects?.*sekaligus",
                r"hapus.*projects?.*secara.*bersamaan",
                r"bulk.*delete.*projects?"
            ]
        }
    }

    # Common typos and variations
    COMMON_VARIATIONS = {
        "create": ["crate", "craete", "creatte", "creat", "buat", "bikin"],
        "project": ["projct", "projecct", "projectt", "porject", "projek", "proyek"],
        "delete": ["delte", "delette", "deelete", "dlete", "hapus"],
        "list": ["lst", "lisst", "liste", "tampil", "lihat"],
        "show": ["shw", "shoow", "schow", "tunjuk"]
    }

    @classmethod
    def detect_intent(cls, command: str) -> Tuple[Optional[str], float, Dict]:
        """
        Detect the intent of a command using fuzzy matching and pattern recognition.

        Args:
            command (str): The command string to analyze

        Returns:
            Tuple[Optional[str], float, Dict]: The detected intent, confidence score, and any extracted parameters
        """
        print(f"Analyzing command: {command}")
        command = command.lower().strip()
        best_intent = None
        best_score = 0.0
        extracted_params = {}

        # Check each intent pattern
        for intent, patterns in cls.INTENT_PATTERNS.items():
            # Check patterns for each language
            for lang_patterns in patterns.values():
                for pattern in lang_patterns:
                    if re.search(pattern, command):
                        score = cls._calculate_pattern_score(pattern, command)
                        print(f"Pattern {pattern} matched with score {score}")
                        if score > best_score:
                            best_score = score
                            best_intent = intent

        # If no strong match found, try fuzzy matching with common variations
        if best_score < 0.6:
            fuzzy_intent, fuzzy_score = cls._check_fuzzy_variations(command)
            if fuzzy_score > best_score:
                best_intent = fuzzy_intent
                best_score = fuzzy_score

        # Extract parameters based on the detected intent
        if best_intent:
            extracted_params = cls._extract_parameters(command, best_intent)
            print(f"Extracted parameters: {extracted_params}")

            # Boost confidence score if we have good parameter extraction
            if extracted_params:
                if "project_id" in extracted_params and best_intent in ["create_project", "delete_project"]:
                    best_score = max(best_score, 0.85)
                elif "environment" in extracted_params and best_intent == "list_projects":
                    best_score = max(best_score, 0.85)

        return best_intent, best_score, extracted_params

    @classmethod
    def _extract_parameters(cls, command: str, intent_type: str) -> Dict:
        """Extract parameters from the command text based on intent type."""
        params = {}

        if intent_type == "delete_project":
            # First check for bulk operation keywords
            bulk_keywords = r'\b(all|semua|multiple|beberapa|banyak)\b'
            if re.search(bulk_keywords, command, re.IGNORECASE):
                params['is_bulk'] = True
                
            # Extract environment if specified
            env_pattern = r'\b(?:in|from|di|dalam)\s+(prod|production|dev|development|staging|test)\b'
            env_match = re.search(env_pattern, command, re.IGNORECASE)
            if env_match:
                params['environment'] = env_match.group(1).lower()

            # Handle project ID extraction for both single and bulk deletion
            project_pattern = r'project\s+([a-zA-Z0-9-]+(?:\s*(?:,|dan|and)\s*[a-zA-Z0-9-]+)*)'
            matches = re.search(project_pattern, command, re.IGNORECASE)
            
            if matches:
                # Clean and split project IDs
                project_ids_raw = matches.group(1).strip()
                # Split on commas and/or 'and'/'dan', handle multiple spaces
                project_ids = re.split(r'\s*(?:,|dan|and)\s*', project_ids_raw)
                # Clean each ID and filter out empty strings and common words
                project_ids = [
                    pid.strip() 
                    for pid in project_ids 
                    if pid.strip() and pid.strip().lower() not in ['dan', 'and', 'boleh', 'ya', 'yes']
                ]
                
                if len(project_ids) > 1:
                    params['project_ids'] = project_ids
                    params['is_bulk'] = True
                elif project_ids:
                    params['project_id'] = project_ids[0]
                    params['is_bulk'] = False

        elif intent_type == "create_project":
            # Handle project ID extraction for both single and bulk creation
            project_pattern = r'project\s+(?:baru\s+)?([a-zA-Z0-9-]+(?:\s*(?:,|dan|and)\s*[a-zA-Z0-9-]+)*)'
            matches = re.search(project_pattern, command, re.IGNORECASE)
            
            if matches:
                # Clean and split project IDs
                project_ids_raw = matches.group(1).strip()
                # Split on commas and/or 'and'/'dan'
                project_ids = re.split(r'\s*(?:,|dan|and)\s*', project_ids_raw)
                # Clean each ID and filter out empty strings and common words
                project_ids = [
                    pid.strip() 
                    for pid in project_ids 
                    if pid.strip() and pid.strip().lower() not in ['dan', 'and', 'boleh', 'ya', 'yes']
                ]
                
                if len(project_ids) > 1:
                    params['project_ids'] = project_ids
                    params['is_bulk'] = True
                elif project_ids:
                    params['project_id'] = project_ids[0]
                    params['is_bulk'] = False

                # Try to extract display name if provided
                # Support both English and Indonesian formats
                name_patterns = [
                    # English patterns
                    r'(?:with\s+name|named)\s+["\']?([^"\']+)["\']?',
                    # Indonesian patterns - handle both "dengan nama" and just "dengan"
                    r'dengan(?:\s+nama)?\s+["\']?([^"\']+)["\']?'
                ]
                
                for pattern in name_patterns:
                    name_match = re.search(pattern, command, re.IGNORECASE)
                    if name_match:
                        project_name = name_match.group(1).strip()
                        # Clean up the project name by removing common trailing words
                        project_name = re.sub(r'\s*(?:ya|aja|saja|please|thanks)\s*$', '', project_name, flags=re.IGNORECASE)
                        params['project_name'] = project_name
                        break

        return params

    @classmethod
    def _calculate_pattern_score(cls, pattern: str, command: str) -> float:
        """Calculate a confidence score for a pattern match."""
        # Remove regex special characters for comparison
        clean_pattern = re.sub(r'[.*?+]', '', pattern)
        
        # Special handling for Indonesian patterns
        if any(word in command for word in ["buat", "bikin", "dengan"]):
            if "project" in clean_pattern and ("buat" in clean_pattern or "bikin" in clean_pattern):
                return 0.9
                
        return SequenceMatcher(None, clean_pattern, command).ratio()

    @classmethod
    def _check_fuzzy_variations(cls, command: str) -> Tuple[Optional[str], float]:
        """Check command against common variations and typos."""
        best_score = 0.0
        best_intent = None

        # Check each word in the command against our variations
        command_words = command.split()
        for word in command_words:
            for key, variations in cls.COMMON_VARIATIONS.items():
                for variation in variations:
                    score = SequenceMatcher(None, word, variation).ratio()
                    if score > 0.8:  # High similarity threshold
                        # Map back to intent
                        if key in ["create", "new"]:
                            return "create_project", score
                        elif key in ["delete", "remove"]:
                            return "delete_project", score
                        elif key in ["list", "show"]:
                            return "list_projects", score

        return best_intent, best_score

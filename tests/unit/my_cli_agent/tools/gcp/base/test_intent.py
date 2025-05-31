"""Unit tests for GCP intent detection."""
import pytest
from my_cli_agent.tools.gcp.base.intent import IntentDetector

class TestIntentDetector:
    """Test suite for intent detection functionality."""
    
    def test_list_projects_intent(self):
        """Test detection of list projects intent in different languages."""
        test_cases = [
            # English variations
            ("list gcp projects", "list_projects", "all"),
            ("show me all projects", "list_projects", "all"),
            ("get projects in dev", "list_projects", "dev"),
            ("display staging projects", "list_projects", "staging"),
            
            # Indonesian variations
            ("tampilkan projects", "list_projects", "all"),
            ("lihat project dev", "list_projects", "dev"),
            ("berapa projects yang ada", "list_projects", "all"),
            ("daftar project staging", "list_projects", "staging"),
            
            # With typos
            ("lst projects", "list_projects", "all"),
            ("lisst all projects", "list_projects", "all"),
            ("shw projects dev", "list_projects", "dev")
        ]
        
        for command, expected_intent, expected_env in test_cases:
            intent, score, params = IntentDetector.detect_intent(command)
            assert intent == expected_intent
            assert score >= 0.6
            assert params.get("environment") == expected_env
            
    def test_create_project_intent(self):
        """Test detection of create project intent in different languages."""
        test_cases = [
            # English variations
            ("create gcp project test-proj-1", "create_project", "test-proj-1", None),
            ("new project test-proj-2 Test Project", "create_project", "test-proj-2", "Test Project"),
            
            # Indonesian variations
            ("buat project test-proj-3", "create_project", "test-proj-3", None),
            ("bikin project test-proj-4 Project Baru", "create_project", "test-proj-4", "Project Baru"),
            
            # With typos
            ("crate project test-proj-5", "create_project", "test-proj-5", None),
            ("craete project test-proj-6", "create_project", "test-proj-6", None)
        ]
        
        for command, expected_intent, expected_id, expected_name in test_cases:
            intent, score, params = IntentDetector.detect_intent(command)
            assert intent == expected_intent
            assert score >= 0.6
            assert params.get("project_id") == expected_id
            if expected_name:
                assert params.get("project_name") == expected_name
                
    def test_delete_project_intent(self):
        """Test detection of delete project intent in different languages."""
        test_cases = [
            # English variations
            ("delete gcp project test-proj-1", "delete_project", "test-proj-1"),
            ("remove project test-proj-2", "delete_project", "test-proj-2"),
            
            # Indonesian variations
            ("hapus project test-proj-3", "delete_project", "test-proj-3"),
            
            # With typos
            ("delte project test-proj-4", "delete_project", "test-proj-4"),
            ("delette project test-proj-5", "delete_project", "test-proj-5")
        ]
        
        for command, expected_intent, expected_id in test_cases:
            intent, score, params = IntentDetector.detect_intent(command)
            assert intent == expected_intent
            assert score >= 0.6
            assert params.get("project_id") == expected_id
            
    def test_low_confidence_cases(self):
        """Test cases that should return low confidence scores."""
        test_cases = [
            "invalid command",
            "show me the money",
            "random text",
            "project",  # too ambiguous
        ]
        
        for command in test_cases:
            _, score, _ = IntentDetector.detect_intent(command)
            assert score < 0.6
            
    def test_multilingual_support(self):
        """Test support for mixed language commands."""
        test_cases = [
            # Mixed English-Indonesian
            ("tampilkan all projects", "list_projects"),
            ("create project baru", "create_project"),
            ("hapus gcp project", "delete_project"),
        ]
        
        for command, expected_intent in test_cases:
            intent, score, _ = IntentDetector.detect_intent(command)
            assert intent == expected_intent
            assert score >= 0.6
            
    def test_parameter_extraction(self):
        """Test extraction of command parameters."""
        # Test project ID and name extraction
        intent, _, params = IntentDetector.detect_intent(
            "create project test-proj-1 My Test Project"
        )
        assert intent == "create_project"
        assert params["project_id"] == "test-proj-1"
        assert params["project_name"] == "My Test Project"
        
        # Test environment extraction
        intent, _, params = IntentDetector.detect_intent(
            "list projects in staging"
        )
        assert intent == "list_projects"
        assert params["environment"] == "staging"
        
        # Test project ID extraction for deletion
        intent, _, params = IntentDetector.detect_intent(
            "delete project test-proj-2"
        )
        assert intent == "delete_project"
        assert params["project_id"] == "test-proj-2"

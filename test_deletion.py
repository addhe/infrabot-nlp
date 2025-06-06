#!/usr/bin/env python3
"""Simple script to test the delete_vpc_network function."""
from unittest.mock import patch
from adk_cli_agent.tools.gcp_vpc import delete_vpc_network

print("Starting test script...")

@patch("adk_cli_agent.tools.gcp_vpc.confirm_action", return_value=False)
def test_cancellation(mock_confirm):
    """Test user cancellation path."""
    print("Running cancellation test...")
    try:
        result = delete_vpc_network(
            project_id="test-project",
            network_name="test-vpc"
        )
        print("Result:", result)
        print(f"Status: {result['status']} (Expecting 'cancelled')")
        assert result["status"] == "cancelled", f"Expected 'cancelled' but got '{result['status']}'"
        print("Test passed!")
    except Exception as e:
        print(f"Test failed with exception: {e}")
        raise

print("About to run test function...")

if __name__ == "__main__":
    print("In __main__ block")
    test_cancellation()
    print("Test execution complete")

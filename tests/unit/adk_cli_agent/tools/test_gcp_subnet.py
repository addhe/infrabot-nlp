import pytest
from adk_cli_agent.tools.gcp_subnet import list_subnets

class DummyNetwork:
    def __init__(self, name="default", id="id-1"):
        self.name = name
        self.id = id
        self.subnets = [
            {
                "name": "subnet-1",
                "region": "us-central1",
                "cidr_range": "10.0.0.0/24",
                "private_google_access": True
            },
            {
                "name": "subnet-2",
                "region": "asia-southeast1",
                "cidr_range": "10.1.0.0/24",
                "private_google_access": False
            }
        ]

# Patch get_vpc_details to simulate backend
@pytest.fixture
def patch_get_vpc_details(monkeypatch):
    def fake_get_vpc_details(project_id, network_name):
        if project_id == "fail-proj":
            return {"status": "error", "message": "fail", "details": "fail details"}
        return {
            "status": "success",
            "network": {
                "name": network_name,
                "id": "id-1",
                "subnets": DummyNetwork().subnets
            }
        }
    monkeypatch.setattr("adk_cli_agent.tools.gcp_subnet.get_vpc_details", fake_get_vpc_details)


def test_list_subnets_success(patch_get_vpc_details):
    result = list_subnets("my-proj", "default")
    assert result["status"] == "success"
    assert isinstance(result["subnets"], list)
    assert len(result["subnets"]) == 2
    assert result["subnets"][0]["name"] == "subnet-1"
    assert result["subnets"][1]["region"] == "asia-southeast1"

def test_list_subnets_error(patch_get_vpc_details):
    result = list_subnets("fail-proj", "default")
    assert result["status"] == "error"
    assert "Failed to get VPC details" in result["message"]
    assert result["details"] == "fail details"

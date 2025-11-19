"""
Quick API test script
"""
import sys
sys.path.insert(0, '/home/user/ccw-hvac_model/backend')

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    """Test health endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("✓ Health check passed")

def test_presets():
    """Test presets endpoint"""
    response = client.get("/api/v1/presets")
    assert response.status_code == 200
    data = response.json()
    assert "presets" in data
    assert len(data["presets"]) == 2
    print(f"✓ Presets endpoint passed - found {len(data['presets'])} presets")

def test_modern_preset():
    """Test modern preset endpoint"""
    response = client.get("/api/v1/presets/modern")
    if response.status_code != 200:
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "最新オフィス"
    print(f"✓ Modern preset passed - {data['name']}")

def test_old_preset():
    """Test old preset endpoint"""
    response = client.get("/api/v1/presets/old")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "旧式オフィス"
    print(f"✓ Old preset passed - {data['name']}")

def test_simulation():
    """Test simulation endpoint"""
    # Get modern preset
    preset_response = client.get("/api/v1/presets/modern")
    preset = preset_response.json()

    # Run simulation
    response = client.post("/api/v1/simulate", json={
        "floor_spec": preset["floor_spec"],
        "equipment_spec": preset["equipment_spec"],
        "monthly_conditions": preset["monthly_conditions"]
    })

    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "summary" in data
    assert len(data["results"]) == 12

    print(f"✓ Simulation passed - {len(data['results'])} months")
    print(f"  Annual central: {data['summary']['annual_central_total_kWh']:,.0f} kWh")
    print(f"  Annual local: {data['summary']['annual_local_total_kWh']:,.0f} kWh")

if __name__ == "__main__":
    print("="*60)
    print("Running Backend API Tests")
    print("="*60)
    print()

    try:
        test_health()
        test_presets()
        test_modern_preset()
        test_old_preset()
        test_simulation()

        print()
        print("="*60)
        print("All tests passed! ✓")
        print("="*60)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

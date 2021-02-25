class TestHealth:
    def test_health(self, client):
        res = client.get("/health")
        data = res.get_json()

        assert data["data"]["status"] == "running"

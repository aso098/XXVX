from locust import HttpUser, task, between

class DefensiveLoadTest(HttpUser):
    wait_time = between(0.5, 1.5)
    
    @task(3)
    def normal_request(self):
        self.client.get("/")
    
    @task(1)
    def slow_request(self):
        self.client.get("/", headers={"User-Agent": "Test"}, timeout=2)

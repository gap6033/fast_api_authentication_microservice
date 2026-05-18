from locust import HttpUser, task, between, TaskSet
from faker import Faker
import random
import time


class SequentialTaskSet(TaskSet):

    def on_start(self):
        self.fake = Faker()
        self.token = None
        

    @task
    def run_tasks(self):
        self.email = self.fake.email()
        self.password = self.fake.password()
        self.register()
        time.sleep(random.uniform(1, 3))
        self.login()
        time.sleep(random.uniform(1, 3))
        self.logout()
        time.sleep(random.uniform(1, 3))
        self.delete()
        time.sleep(random.uniform(1, 3))
        self.login()
        time.sleep(random.uniform(1, 3))
        self.delete()
        time.sleep(random.uniform(1, 3))
        self.login()
        time.sleep(random.uniform(1, 3))

    def register(self):
        response = self.client.post("/v1/auth/register", json={
            "email": self.email,
            "password": self.password
        })
        if response.status_code != 200:
            print("Registration failed:", response.status_code, response.text)
        else:
            print("Registration successful:", response.status_code, response.text)

    
    def login(self):
        response = self.client.post("/v1/auth/login", json={
            "email": self.email,
            "password": self.password
        })

        if response.status_code == 200:
            self.token = response.json().get("access_token") 
            print("Login successful:", response.status_code, response.text) # adjust if your token key is different
        else:
            print("Login failed:", response.status_code, response.text)

    def logout(self):
        if not self.token:
            return

        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.client.post("/v1/auth/logout", headers=headers)

        if response.status_code != 200:
            print("Logout Failed:", response.status_code, response.text)
        else:
            print("Logout Succesful:", response.status_code, response.text)



    def delete(self):
        if not self.token:
            return

        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.client.delete("/v1/auth/delete", headers=headers)

        if response.status_code != 200:
            print("Delete failed:", response.status_code, response.text)
        else:
            print("Delete successful:", response.status_code, response.text)

   

class SequentialUser(HttpUser):
    tasks = [SequentialTaskSet]
    wait_time = between(1, 2)
import requests
from .types import *

class Client:
    def __init__(self, token: str):
        self.token = token
  
    def call(self, method, path, **kwargs):
        ret = requests.request(method, f"https://poses.live{path}", headers={"Authorization": f"Bearer {self.token}"}, **kwargs)
        ret.raise_for_status()
        return ret.json()
  
    def hello(self):
        return self.call("GET", "/api/hello")

    def get_problem(self, problem_id):
        return Problem.from_dict(self.call("GET", f"/api/problems/{problem_id}"))

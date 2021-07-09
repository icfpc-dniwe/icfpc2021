import requests
from .types import *

class Client:
    def __init__(self, token: str):
        self.token = token
  
    def _call(self, method, path, **kwargs):
        ret = requests.request(method, f"https://poses.live{path}", headers={"Authorization": f"Bearer {self.token}"}, **kwargs)
        ret.raise_for_status()
        return ret.json()
  
    def hello(self):
        self._call("GET", "/api/hello")

    def get_problem(self, problem_id: int):
        return Problem.from_dict(self._call("GET", f"/api/problems/{problem_id}"))

    def post_solution(self, problem_id: int, solution: Solution):
        self._call("POST", f"/api/problems/{problem_id}/solutions", json=solution.to_dict())

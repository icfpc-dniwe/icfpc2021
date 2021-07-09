import requests

class Client:
    def __init__(self, token: str):
        self.token = token
  
    def call(self, method, path, **kwargs):
        ret = requests.request(f"https://poses.live{path}", method=method, headers={"Authorization": f"Bearer {self.token}"}, **kwargs)
        ret.raise_on_error()
        return ret.json()
  
    def hello(self):
        return self.call("GET", "/api/hello")

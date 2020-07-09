import requests


requests.post("http://localhost:8688/alarm",json={"title":"测试","content":"测试内容"})
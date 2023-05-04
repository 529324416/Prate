

import requests


requests.post("http://localhost:5000/alarm", json={"title": "这里是闹钟的标题", "info": "这里是闹钟的文本..."})
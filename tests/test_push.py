# -*- coding: utf-8 -*-
import random
import requests

url = 'http://localhost:9012/push'
data = dict(
    channel_id='123123',
    data=dict(
        ran=random.randint(1, 10)
    )
)
r = requests.post(url, json=data)

print(r.text)

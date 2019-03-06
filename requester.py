import requests
import json


class Requester:
    def __init__(self, url):
        self.url = url



    def post_request(self, payload):
        r = requests.post(self.url, data=json.dumps(payload))
        return r
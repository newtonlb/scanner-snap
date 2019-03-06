import requests


class Requester:
    def __init__(self, url):
        self.url = url



    def post_request(self, payload):
        r = requests.post(self.url, data=payload)
        return r
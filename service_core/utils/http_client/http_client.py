import logging
from typing import Dict

import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter


class HTTPClient:

    def __init__(self, url, apikey):
        self.url = url
        self.s = requests.Session()
        retries = Retry(total=5,
                        backoff_factor=0.1,
                        status_forcelist=[500, 502, 503, 504])
        self.s.mount('http://', HTTPAdapter(max_retries=retries))
        self.s.mount('https://', HTTPAdapter(max_retries=retries))
        self.headers = {
            "x-api-key": apikey
        }

    def call(self, method: str = "post", body: Dict = {}):
        handler = getattr(self.s, method.lower())
        return handler(self.url, json=body, headers=self.headers)

import requests
from requests_objc_adapter.adapters import NSURLSessionAdapter


def test_basic():
    session = requests.session()
    session.mount('http://', NSURLSessionAdapter())

    session.get('http://localhost')
    
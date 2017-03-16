import requests
from requests_objc_adapter.adapters import URLSessionAdapter

def test_basic():
    session = requests.session()
    session.mount('/', URLSessionAdapter())

    session.get('http://localhost')
    
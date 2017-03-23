
import requests
from requests_objc_adapter.adapters import NSURLSessionAdapter


def test_basic():
    session = requests.session()
    session.mount('http://', NSURLSessionAdapter())

    session.get('http://localhost')


def test_post():
    """Test form urlencoded"""
    session = requests.session()
    session.mount('http://', NSURLSessionAdapter())

    payload = {'key1': 'value1', 'key2': 'value2'}
    session.post('http://localhost', data=payload)


import pytest
import requests
from requests_objc_adapter.adapters import NSURLSessionAdapter


@pytest.fixture
def session():
    s = requests.session()
    s.mount('http://', NSURLSessionAdapter())
    s.mount('https://', NSURLSessionAdapter())
    return s


class TestRequestsNSURLSessionDelegate(object):

    def test_verify_false(self, session):
        """Ignore invalid SSL certificates by trusting the SecTrustRef given."""
        session.verify = False
        response = session.get('https://localhost:8444')
        

# -*- coding: utf-8 -*-
"""
Defines the Requests Transport Adapter that uses NSURLSession.
"""
import objc

from requests.adapters import BaseAdapter
from requests.models import Response

from Foundation import NSMutableURLRequest, NSURL, NSURLRequestUseProtocolCachePolicy, \
    NSURLRequestReloadIgnoringLocalCacheData, NSURLRequestReturnCacheDataElseLoad, \
    NSURLSessionConfiguration, NSURLSession, NSOperationQueue

from delegates import RequestsNSURLSessionDataDelegate

# These headers are reserved to the NSURLSession and should not be set by
# Requests, though we may use them.
_RESERVED_HEADERS = set([
    'authorization', 'connection', 'host', 'proxy-authenticate',
    'proxy-authorization', 'www-authenticate',
])

try:
    from Queue import Queue
except ImportError:  #py3
    from queue import Queue

def _build_NSRequest(request, timeout):
    """
    Converts a Requests request into an NSMutableURLRequest. Does not touch the
    request body: that's handled elsewhere.

    Args:
          request: Request object
          timeout: Request timeout
    Returns:
          Instance of NSMutableURLRequest
    """
    nsrequest = NSMutableURLRequest.requestWithURL_(
        NSURL.URLWithString_(request.url)
    )
    nsrequest.setHTTPMethod_(request.method)

    # if request.body is not None:  # Non multipart only
    #     nsrequest.setHTTPBody_(request.body)

    if timeout is not None:
        nsrequest.timeoutInterval = float(timeout)

    for k, v in request.headers.items():
        k, v = k.lower(), v.lower()

        if k in _RESERVED_HEADERS:
            continue

        nsrequest.setValue_forHTTPHeaderField_(v, k)

    return nsrequest


class NSURLSessionAdapter(BaseAdapter):
    """NSURLSession Transport Adapter

    Requests doesn't directly implement anything like the cache policy, so this is ignored for now.
    """

    def __init__(self):
        super(NSURLSessionAdapter, self).__init__()

        self._delegate = None
        self._session = None
        self._request = None
        self._queue = None
        
        self._initialize_session()

    def _initialize_session(self):
        """Set up the NSURLSessionConfiguration"""
        configuration = NSURLSessionConfiguration.defaultSessionConfiguration()
        self._delegate = RequestsNSURLSessionDataDelegate.alloc().initWithAdapter_(self)
        self._session = (
            NSURLSession.sessionWithConfiguration_delegate_delegateQueue_(
                configuration,
                self._delegate,
                None,
            )
        )

    def receive_error(self, task, error):
        """
        Called by the delegate when a error has occurred.
        This call is expected only on background threads, and thus may not do
        anything that is not Python-thread-safe. This means that, for example,
        it is safe to grab things from the _tasks dictionary, but it is not
        safe to make other method calls on this object unless they explicitly
        state that they are safe in background threads.
        """
        # TODO: Better exceptions!
        exception = Exception(error.localizedDescription)
        self._queue.put_nowait((None, exception))

    def receive_response(self, task, response):
        """
        Called by the delegate when a response has been received.
        This call is expected only on background threads, and thus may not do
        anything that is not Python-thread-safe. This means that, for example,
        it is safe to grab things from the _tasks dictionary, but it is not
        safe to make other method calls on this object unless they explicitly
        state that they are safe in background threads.
        """
        resp = Response()
        resp.status_code = response.statusCode
        resp.reason = ''

        # TODO: This needs to point to an object that we can use to provide
        # the various raw things that requests needs.
        resp.raw = None

        resp.connection = self

        # Put this response on the queue.
        self._queue.put_nowait((resp, None))


    def send(self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None):
        """Sends PreparedRequest object. Returns Response object.

        :param request: The :class:`PreparedRequest <PreparedRequest>` being sent.
        :param stream: (optional) Whether to stream the request content.
        :param timeout: (optional) How long to wait for the server to send
            data before giving up, as a float, or a :ref:`(connect timeout,
            read timeout) <timeouts>` tuple.
        :type timeout: float or tuple
        :param verify: (optional) Whether to verify SSL certificates.
        :param cert: (optional) Any user-provided SSL certificate to be trusted.
        :param proxies: (optional) The proxies dictionary to apply to the request.
        :rtype: requests.Response
        """
        nsrequest = _build_NSRequest(request, timeout)


        # TODO: Support all of this stuff.
        assert not stream
        assert verify  # see https://developer.apple.com/library/content/documentation/NetworkingInternet/Conceptual/NetworkingTopics/Articles/OverridingSSLChainValidationCorrectly.html#//apple_ref/doc/uid/TP40012544-SW6
        assert not cert
        assert not proxies

        self._queue = Queue()
        if request.method in ['PUT', 'POST']:
            # These verbs should usually be an upload task to send the correct request headers.
            task = self._session.uploadTaskWithRequest_fromData_(nsrequest, request.body)
        else:
            task = self._session.dataTaskWithRequest_(nsrequest)

        task.resume()

        response, error = self._queue.get()

        if error is not None:
            raise error

        return response

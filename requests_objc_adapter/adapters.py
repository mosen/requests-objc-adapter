from requests.adapters import BaseAdapter
from Foundation import NSMutableURLRequest, NSURL, NSURLRequestUseProtocolCachePolicy, \
    NSURLRequestReloadIgnoringLocalCacheData, NSURLRequestReturnCacheDataElseLoad, \
    NSURLSessionConfiguration, NSURLSession, NSOperationQueue

class URLSessionAdapter(BaseAdapter):
    """NSURLSession Transport Adapter

    Requests doesn't directly implement anything like the cache policy, so this is ignored for now.
    """

    def __init__(self):
        super(URLSessionAdapter, self).__init__()

    def _prepare_nsurlrequest(self, request, timeout=10):
        """Generate an instance of NSURLRequest from a requests PreparedRequest() instance.

        :param request: The :class:`PreparedRequest <PreparedRequest>` being sent.
        :param timeout: (optional) How long to wait for the server to send
            data before giving up, as a float, or a :ref:`(connect timeout,
            read timeout) <timeouts>` tuple.
        """
        url = NSURL.URLWithString_(request.url)

        urlrequest = NSMutableURLRequest.requestWithURL_cachePolicy_timeoutInterval_(
            url,
            NSURLRequestUseProtocolCachePolicy,
            int(timeout)
        )

        return urlrequest

    def _prepare_nsurlsessionconfiguration(self, request, timeout):
        urlsessionconfiguration = NSURLSessionConfiguration.defaultSessionConfiguration()
        return urlsessionconfiguration

    def add_headers(self, request, urlrequest):
        """Add any headers needed by the connection.

        :param request: The :class:`PreparedRequest <PreparedRequest>` to add headers from.
        :param urlrequest: The `NSURLRequest` to add headers to.
        """
        for header, value in request.headers.items():
            urlrequest.addValue_forHTTPHeaderField_(value, header)

    def _prepare_auth(self):
        """TODO: NSURLProtectionSpace, currently not needed as Authorization is shoved into headers for basic"""
        pass

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
        if isinstance(timeout, tuple):
            timeout, = timeout  # only the connect timeout is used

        urlrequest = self._prepare_nsurlrequest(request, timeout)
        self.add_headers(request, urlrequest)
        session_config = self._prepare_nsurlsessionconfiguration(request, 0)

        operation_queue = NSOperationQueue.mainQueue()

        session = NSURLSession.sessionWithConfiguration_delegate_delegateQueue(
            session_config,
            self,
            operation_queue
        )

        def completionHandler(data, response, error):
            print('got completion handler')

        task = session.dataTaskWithRequest_completionHandler_(
            urlrequest,
            completionHandler
        )

        task.resume()
        

        

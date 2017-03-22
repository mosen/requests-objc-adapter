# -*- coding: utf-8 -*-
"""
Defines the delegates for the Requests Transport Adapter that uses NSURLSession.
"""
import objc
from Cocoa import NSObject, NSURLAuthenticationMethodServerTrust, NSURLAuthenticationMethodHTTPBasic, NSURLCredential

# objc.registerMetaDataForSelector('NSURLSessionTaskDelegate', 'URLSession:task:didReceiveChallenge:completionHandler:', {
#     "arguments": {
#         3: {
#             "callable": {
#                 "arguments": {
#                     "0": { "typestr": "^v" },
#                     "1": { "typestr": [ "I", "Q" ] }
#                 },
#                 "retval": { "typestr": "v" }
#             }
#         }
#     }
# })

class RequestsNSURLSessionDelegate(NSObject):
    """
    This delegate implements certain callbacks that NSURLSession will make to
    determine bits of information in the middle of requests. This allows
    NSURLSession to return control immediately, while still asking the
    application for more details.
    """
    def initWithAdapter_(self, adapter):
        self = objc.super(RequestsNSURLSessionDelegate, self).init()
        if self is None:
            return None

        # Save a reference to the adapter. This will let us call back into it
        # to handle things.
        self._adapter = adapter
        return self

    def URLSession_task_didReceiveChallenge_completionHandler_(self, session,
                                                               task, challenge,
                                                               handler):
        """
        Requests credentials from the delegate in response to an authentication
        request from the remote server.
        :param session: The session containing the task whose request requires
            authentication.
        :type session: NSURLSession
        :param task: The task whose request requires authentication.
        :type task: NSURLSessionTask
        :param challenge: An object that contains the request for
            authentication.
        :type challenge: NSURLAuthenticationChallenge
        :param handler: A handler that this method calls. Its parameters are:
            - ``disposition``: One of several constants that describes how the
              challenge should be handled.
            - ``credential``: The credential that should be used for
              authentication if disposition is
              ``NSURLSessionAuthChallengeUseCredential``; otherwise, None.
        :type handler: Function taking two arguments. First is of type
            NSURLSessionAuthChallengeDisposition, second is of NSURLCredential.
        :returns: Nothing
        """
        protection_space = challenge.protectionSpace()
        if protection_space.authenticationMethod == NSURLAuthenticationMethodServerTrust:
            if not self._adapter.verify:
                trust = protection_space.serverTrust()
                credential = NSURLCredential.credentialForTrust_(trust)
                handler(1, credential)

        # elif protection_space.authenticationMethod == NSURLAuthenticationMethodHTTPBasic:
        #     handler()

        # TODO: Here we'll handle all of auth, verify, and cert. For now, just
        # do the default.
        # handler(1, None)

    def URLSession_task_didCompleteWithError_(self, session, task, error):
        """
        Tells the delegate that the task finished transferring data.
        Server errors are not reported through the error parameter. The only
        errors this delegate receives through the error parameter are
        client-side errors, such as being unable to resolve the hostname or
        connect to the host.
        :param session: The session containing the task whose request finished
            transferring data.
        :type session: NSURLSession
        :param task: The task whose request finished transferring data.
        :type task: NSURLSessionTask
        :param error: If an error occurred, an error object indicating how the
            transfer failed, otherwise None.
        :type error: NSError or None
        :returns: Nothing
        """
        if error is not None:
            self._adapter.receive_error(task, error)

    # URLSession_task_didSendBodyData_totalBytesSent_totalBytesExpectedToSend_
    # Requests don't care 

    def URLSession_task_willPerformHTTPRedirection_newRequest_completionHandler_(self,
                                                                                 session,
                                                                                 task,
                                                                                 response,
                                                                                 request,
                                                                                 handler):
        """
        Tells the delegate that the remote server requested an HTTP redirect.
        Requests handles its own redirects, so we always refuse. We do this by
        calling the completion handler with ``None``.
        """
        handler(None)

    def URLSession_dataTask_didReceiveResponse_completionHandler_(self,
                                                                  session,
                                                                  dataTask,
                                                                  response,
                                                                  handler):
        """
        Tells the delegate that the data task received the initial reply
        (headers) from the server.
        :param session: The session containing the data task that received an
            initial reply.
        :type session: NSURLSession
        :param task: The data task that received an initial reply.
        :type task: NSURLSessionDataTask
        :param response: A URL response object populated with headers.
        :type response: NSURLResponse
        :param handler: A completion handler that our code calls to continue
            the transfer, passing a constant to indicate whether the transfer
            should continue as a data task or should become a download task.
            - If we pass NSURLSessionResponseAllow, the task continues
              normally.
            - If we pass NSURLSessionResponseCancel, the task is canceled.
            - If we pass NSURLSessionResponseBecomeDownload as the disposition,
              our delegate’s ``URLSession:dataTask:didBecomeDownloadTask:``
              method is called to provide you with the new download task that
              supersedes the current task.
        :type handler: Function that takes one argument, a
            ``NSURLSessionResponseDisposition``.
        :returns: Nothing.
        """
        self._adapter.receive_response(dataTask, response)
        #handler(NSURLSessionResponseAllow)



"""
A simple module that implements a class for working with the FastSpring orders
and subscription API. Each method corresponds to a documented FastSpring API
endpoint. Data is entered and returned as a dict.

https://github.com/fastspring/fastspring-api/

This module relies on Martin Blech's highly useful xmltodict module:
https://github.com/martinblech/xmltodict/

"""
import logging
import urlparse
import xmltodict
import requests
from requests.auth import HTTPBasicAuth


logger = logging.getLogger(__name__)


class FastSpringException(Exception):

    def __init__(self, detail, status, message, reason):
        self.detail, self.status, self.message, self.reason = detail, status, message, reason


class FastSpringAPI(object):

    def __init__(self, username, password, company, api_base_url='https://api.fastspring.com'):
        """
        Initialize the API object. 'username', 'password', and 'company' should
        be provided with your FastSpring account.
        """
        self.username = username
        self.password = password
        self.company = company
        self.api_base_url = api_base_url

    def get_order(self, reference):
        """
        Retrieve an order based on its reference ID. Returns a dict of
        order information on success.

        Failure returns a FastSpringException.
        """
        content, status, message, reason = self._request('GET', 'order/%s' % reference)
        if content:
            return xmltodict.parse(content)
        else:
            raise FastSpringException('Could not get order information', status, message, reason)

    def generate_coupon(self, prefix):
        """
        Generate a cupon with the specified prefix. Returns a dict of the cupon
        information on success.

        Failure raises a FastSpringException.
        """
        content, status, message, reason = self._request('POST', 'coupon/%s/generate' % prefix)
        if content:
            return xmltodict.parse(content)
        else:
            raise FastSpringException('Could not generate coupon', status, message, reason)

    def get_subscription(self, reference):
        """
        Get a dict of subscription information based on a reference ID. Returns
        None on success.

        Failure raises a FastSpringException.
        """
        content, status, message, reason = self._request('GET', 'subscription/%s' % reference)
        return xmltodict.parse(content)

    def update_subscription(self, reference, subscription_data):
        content, status, message, reason = self._request('PUT', 'subscription/%s' % reference, {'subscription': subscription_data})
        if status != 200:
            raise FastSpringException('Could not update subscription', status, message, reason)
        return xmltodict.parse(content)

    def cancel_subscription(self, reference):
        """
        Cancel a subscription based on its reference ID. Returns the
        subscription information on success.

        Failure raises a FastSpringException.
        """
        content, status, message, reason = self._request('DELETE', 'subscription/%s' % reference)
        if content:
            return xmltodict.parse(content)
        elif not status == 200:
            raise FastSpringException('Could not cancel subscription', status, message, reason)

    def renew_subscription(self, reference, simulate = None):
        """
        Renew a subscription based on its reference ID. This method returns a
        four-tuple in the format:

        (<True|False success>, <HTTP status code>, <HTTP message>, <HTTP reason>)
        """
        if simulate:
            data = 'simulate=%s' % simulate
        else:
            data = None

        content, status, message, reason = self._request('POST', 'subscription/%s/renew' % reference, data, skip_unparse = True)
        if status == 200:
            return (True, status, message, reason)
        else:
            return (False, status, message, reason)

    def _request(self, method, path, data=None, skip_unparse=False):
        """
        Internal method for making requests to the FastSpring server.
        """
        if data and not skip_unparse:
            body = xmltodict.unparse(data)
        else:
            body = data

        request_path = '/company/%s/%s' % (self.company, path)
        url = urlparse.urljoin(self.api_base_url, request_path)
        logger.debug(url)
        logger.debug("body: %s", body)
        response = requests.request(
            method,
            url,
            headers={"Content-type": "application/xml"},
            auth=HTTPBasicAuth(self.username, self.password),
            data=body,
            )

        status_code = response.status_code
        content = response.content
        message = ""
        reason = response.reason
        return content, status_code, message, reason

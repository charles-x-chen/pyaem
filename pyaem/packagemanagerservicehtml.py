import json
from urllib.parse import quote_plus

import pycurl
from bs4 import BeautifulSoup

from . import handlers
from . import httprequest as bag
from . import result as res


class PackageManagerServiceHtml(object):
    """Package Manager service using /crx/packmgr/service/script.html AEM endpoint.

    The endpoint's response payload is in HTML format with message embedded in:

    * <textarea>the message</textarea> fragment when status code is 200

    * <div id="message">the message</div> fragment when status code is 201

    The Adobe consultant I worked with advised me that this endpoint provides a 'more synchronous'
    operations compared to its /crx/packmgr/service/.json counterpart.

    Check out PackageManager, PackageManagerServiceJson, and PackageManagerServiceJsp for other
    package-related services.
    """

    def __init__(self, url, **kwargs):

        def _handler_ok(response):

            soup = BeautifulSoup(response['body'],
                                 convertEntities=BeautifulSoup.HTML_ENTITIES
                                 )
            message_elem = soup.find('textarea')
            data = json.loads(message_elem.contents[0])
            message = data['msg']

            result = res.PyAemResult(response)
            if data['success']:
                result.success(message)
            else:
                result.failure(message)
            return result

        def _handler_created(response):

            soup = BeautifulSoup(response['body'],
                                 convertEntities=BeautifulSoup.HTML_ENTITIES
                                 )
            message_elem = soup.find('div', {'id': 'Message'})
            message = message_elem.contents[0]

            result = res.PyAemResult(response)
            result.success(message)
            return result

        self.url = url
        self.kwargs = kwargs
        self.handlers = {
            200: _handler_ok,
            201: _handler_created,
            401: handlers.auth_fail
        }

    def upload_package(self, package_name, package_version, file_path, **kwargs):

        file_name = '{0}-{1}.zip'.format(package_name, package_version)

        params = {
            'cmd': 'upload',
            'package': (pycurl.FORM_FILE, '{0}/{1}'.format(file_path, file_name))
        }

        opts = {
            'file_name': file_name
        }

        url = '{0}/crx/packmgr/service/script.html/'.format(self.url)
        params = dict(params.items() | kwargs.items())
        _handlers = self.handlers
        opts = dict(self.kwargs.items() | opts.items())

        return bag.upload_file(url, params, _handlers, **opts)

    def install_package(self, group_name, package_name, package_version, **kwargs):

        # AEM might respond with '201 Created' after installing a package
        # this is actually a failure since the package status is uploaded but not installed
        def _handler_failure(response):
            message = 'Installation failure, package status is uploaded but not installed'
            result = res.PyAemResult(response)

            result.failure(message)

            return result

        params = {
            'cmd': 'install'
        }

        method = 'post'
        url = '{0}/crx/packmgr/service/script.html/etc/packages/{1}/{2}-{3}.zip'.format(
            self.url, group_name, quote_plus(package_name), package_version)
        params = dict(params.items() | kwargs.items())
        _handlers = {
            201: _handler_failure
        }
        _handlers = dict(self.handlers.items() | _handlers.items())
        opts = self.kwargs

        return bag.request(method, url, params, _handlers, **opts)

    def replicate_package(self, group_name, package_name, package_version, **kwargs):

        params = {
            'cmd': 'replicate'
        }

        method = 'post'
        url = '{0}/crx/packmgr/service/script.html/etc/packages/{1}/{2}-{3}.zip'.format(
            self.url, group_name, package_name, package_version)
        params = dict(params.items() | kwargs.items())
        _handlers = self.handlers
        opts = self.kwargs

        return bag.request(method, url, params, _handlers, **opts)

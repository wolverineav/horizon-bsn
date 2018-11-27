# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging as log

from six.moves import http_client

session_map = {}
HASH_HEADER = 'Floodlight-Verify-Path'


def request(url, prefix="/api/v1/data/controller/", method='GET',
            data='', hashPath=None, host="127.0.0.1:8080", cookie=None):
    headers = {'Content-type': 'application/json'}

    if cookie:
        headers['Cookie'] = 'session_cookie=%s' % cookie

    if hashPath:
        headers[HASH_HEADER] = hashPath

    connection = http_client.HTTPSConnection(host)

    try:
        connection.request(method, prefix + url, data, headers)
        response = connection.getresponse()
        ret = (response.status, response.reason, response.read(),
               response.getheader(HASH_HEADER))
        if response.status >= 300:
            log.info('Controller REQUEST: %s %s:body=%r' %
                     (method, host + prefix + url, data))
            log.info('Controller RESPONSE: status=%d reason=%r, data=%r,'
                     'hash=%r' % ret)
        return ret
    except Exception as e:
        log.error("Controller REQUEST exception: %s" % e)
        raise


def get(cookie, url, server, port, hashPath=None):
    host = "%s:%d" % (server, port)
    return request(url, hashPath=hashPath, host=host, cookie=cookie)


def post(cookie, url, server, port, data, hashPath=None):
    host = "%s:%d" % (server, port)
    return request(url, method='POST', hashPath=hashPath, host=host, data=data,
                   cookie=cookie)


def patch(cookie, url, server, port, data, hashPath=None):
    host = "%s:%d" % (server, port)
    return request(url, method='PATCH', hashPath=hashPath, host=host,
                   data=data, cookie=cookie)


def put(cookie, url, server, port, data, hashPath=None):
    host = "%s:%d" % (server, port)
    return request(url, method='PUT', hashPath=hashPath, host=host, data=data,
                   cookie=cookie)


def delete(cookie, url, server, port, hashPath=None):
    host = "%s:%d" % (server, port)
    return request(url, method='DELETE', hashPath=hashPath, host=host,
                   cookie=cookie)

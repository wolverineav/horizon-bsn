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

from django.conf.urls import include  # noqa
from django.conf.urls import url  # noqa
from horizon_bsn.content.connections.network_template \
    import admin_urls as network_template_urls
from horizon_bsn.content.connections import urls as purl
from horizon_bsn.content.connections_admin.views import IndexView
import os

LIB_PATH = os.path.join(os.path.abspath(os.path.dirname(purl.__file__)),
                        'templates', 'connections', 'lib')

JS_PATH = os.path.join(os.path.abspath(os.path.dirname(purl.__file__)),
                       'templates', 'connections', 'js')

CSS_PATH = os.path.join(os.path.abspath(os.path.dirname(purl.__file__)),
                        'templates', 'connections', 'css')

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'network_template_admin/',
        include(network_template_urls, namespace='network_template_admin')),
    # url(r'^lib/(?P<path>.*)$', 'django.views.static.serve',
    #     {'document_root': LIB_PATH, 'show_indexes': True}),
    # url(r'^js/(?P<path>.*)$', 'django.views.static.serve',
    #     {'document_root': JS_PATH, 'show_indexes': True}),
    # url(r'^css/(?P<path>.*)$', 'django.views.static.serve',
    #     {'document_root': CSS_PATH, 'show_indexes': True}),
]

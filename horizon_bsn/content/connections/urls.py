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
from django.conf.urls import patterns  # noqa
from django.conf.urls import url  # noqa

from horizon_bsn.content.connections.network_template \
    import urls as network_template_urls
from horizon_bsn.content.connections.reachability_tests \
    import urls as reachability_tests_urls
from horizon_bsn.content.connections.tenant_policies \
    import urls as tenant_policies_urls
from horizon_bsn.content.connections import views

import os

CSS_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                        'templates', 'connections', 'css')
JS_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                       'templates', 'connections', 'js')
LIB_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                        'templates', 'connections', 'lib')

urlpatterns = patterns(
    '',
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'reachability_tests/',
        include(reachability_tests_urls, namespace='reachability_tests')),
    url(r'network_template/',
        include(network_template_urls, namespace='network_template')),
    url(r'tenant_policies/',
        include(tenant_policies_urls, namespace='tenant_policies')),
    url(r'^css/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': CSS_PATH, 'show_indexes': True}),
    url(r'^js/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': JS_PATH, 'show_indexes': True}),
    url(r'^lib/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': LIB_PATH, 'show_indexes': True}),
)

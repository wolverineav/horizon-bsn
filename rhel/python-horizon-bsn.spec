%global pypi_name horizon-bsn
%global pypi_name_underscore horizon_bsn
%global rpm_name horizon-bsn
%global docpath doc/build/html
%global lib_dir %{buildroot}%{python2_sitelib}/%{pypi_name}/plugins/bigswitch

Name:           python-%{rpm_name}
Version:        20151.36.1
Release:        1%{?dist}
Summary:        Big Switch Networks horizon plugin for OpenStack
License:        ASL 2.0
URL:            https://pypi.python.org/pypi/%{pypi_name}
Source0:        https://pypi.python.org/packages/source/b/%{pypi_name}/%{pypi_name}-%{version}.tar.gz
BuildArch:      noarch

Requires:   pytz
Requires:   python-lockfile
Requires:   python-six
Requires:   python-pbr
Requires:   python-django
Requires:   python-django-horizon

BuildRequires: python-django
BuildRequires: python2-devel
BuildRequires: python-setuptools
BuildRequires: python-d2to1
BuildRequires: python-pbr
BuildRequires: python-lockfile
BuildRequires: python-eventlet
BuildRequires: python-six
BuildRequires: gettext
BuildRequires: python-oslo-sphinx >= 2.3.0
BuildRequires: python-netaddr
BuildRequires: python-kombu
BuildRequires: python-anyjson
BuildRequires: python-iso8601

%description
This package contains Big Switch
Networks horizon plugin

%prep
%setup -q -n %{pypi_name}-%{version}

%build
export PBR_VERSION=%{version}
export SKIP_PIP_INSTALL=1
%{__python2} setup.py build
%{__python2} setup.py build_sphinx
rm %{docpath}/.buildinfo

%install
%{__python2} setup.py install --skip-build --root %{buildroot}
mkdir -p %{lib_dir}/tests
for lib in %{lib_dir}/version.py %{lib_dir}/tests/test_server.py; do
    sed '1{\@^#!/usr/bin/env python@d}' $lib > $lib.new &&
    touch -r $lib $lib.new &&
    mv $lib.new $lib
done


%files
%license LICENSE
%{python2_sitelib}/%{pypi_name}
%{python2_sitelib}/%{pypi_name_underscore}
%{python2_sitelib}/%{pypi_name_underscore}-%{version}-py?.?.egg-info

%post

%preun

%postun

%changelog
* Thu Jun 23 2016 Aditya Vaja <wolverine.av@gmail.com> - 20151.36.1
- BVS-6497: present a warning when policy change doesn't affect existing policy set
* Fri Jun 17 2016 xin wu <xin.wu@bigswitch.com> - 20151.36.0
- use new version scheme os_release.bcf_release.bug_fix
* Fri Jun 10 2016 Aditya Vaja <wolverine.av@gmail.com> - 2015.1.2
- BVS-6323 limit testpath visiblity to tenants
* Tue Jun 07 2016 Aditya Vaja <wolverine.av@gmail.com> - 2015.1.1
- Release 2015.1.1 package for kilo_v2

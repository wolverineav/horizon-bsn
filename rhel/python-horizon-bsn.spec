%global pypi_name horizon-bsn
%global pypi_name_underscore horizon_bsn
%global rpm_name horizon-bsn
%global docpath doc/build/html
%global lib_dir %{buildroot}%{python2_sitelib}/%{pypi_name}/plugins/bigswitch

Name:           python-%{rpm_name}
Version:        0.0.35
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
* Wed Aug 29 2018 Aditya Vaja <wolverine.av@gmail.com> - 0.0.35
- add Dockerfile for RHOSP container build and license info for dependencies
* Tue Mar 13 2018 Aditya Vaja <wolverine.av@gmail.com> - 0.0.34
- container customization changes
* Thu Feb 08 2018 Aditya Vaja <wolverine.av@gmail.com> - 0.0.33
- BCF-9905: fix superclass deprecations causing error during horizon startup
* Tue Oct 24 2017 Aditya Vaja <wolverine.av@gmail.com> - 0.0.32
- OSP-17: move policies from router to tenant + L4 ACL
* Fri Oct 20 2017 Aditya Vaja <wolverine.av@gmail.com> - 0.0.31
- show logical path for testpath
* Mon Aug 28 2017 Aditya Vaja <wolverine.av@gmail.com> - 0.0.30
- build changes
* Tue Jun 13 2017 Aditya Vaja <wolverine.av@gmail.com> - 0.0.29
- OSP-36: missed a replacement for quicktest tenant get
* Mon Jun 05 2017 Aditya Vaja <wolverine.av@gmail.com> - 0.0.28
- OSP-36: member user should be able to create reachability test
* Mon Apr 17 2017 Aditya Vaja <wolverine.av@gmail.com> - 0.0.27
- BVS-4634: internationalize text
* Fri Feb 3 2017 Aditya Vaja <wolverine.av@gmail.com> - 0.0.26
- OSP-26 check for presence of routers
* Thu Jan 26 2017 Aditya Vaja <wolverine.av@gmail.com> - 0.0.25
- OSP-19 ensure policy is deleted in MLR case
* Thu Jan 19 2017 Aditya Vaja <wolverine.av@gmail.com> - 0.0.24
- OSP-6 handle MLR in horizon
* Fri Nov 18 2016 Aditya Vaja <wolverine.av@gmail.com> - 0.0.23
- BVS-6565 router policy look and feel enhancements
* Fri Sep 2 2016 Aditya Vaja <wolverine.av@gmail.com> - 0.0.22
- move angular enabled files to future_enabled
* Mon Aug 29 2016 Michael Xiong <mmxiong@ucla.edu> - 0.0.21
- BVS-6759: move horizon dashboard to use the new AngularJS framework
* Thu Jun 23 2016 Aditya Vaja <wolverine.av@gmail.com> - 0.0.20
- BVS-6497: present a warning when policy change doesn't affect existing policy set
* Fri Jun 10 2016 Aditya Vaja <wolverine.av@gmail.com> - 0.0.19
- BVS-6323 limit testpath visiblity to tenants
* Tue May 24 2016 Aditya Vaja <wolverine.av@gmail.com> - 0.0.18
- ensure quick testpath names are unique
* Tue May 17 2016 Aditya Vaja <wolverine.av@gmail.com> - 0.0.17
- BVS-3794 correct the modal for conflicting rules
* Mon May 16 2016 Aditya Vaja <wolverine.av@gmail.com> - 0.0.16
- BVS-5473 replace occurances of rule with policy
- BVS-5785 fix tenant choices in quick test
* Mon May 16 2016 Aditya Vaja <wolverine.av@gmail.com> - 0.0.15
- tweak build script for upload to pypi
* Thu May 12 2016 Aditya Vaja <wolverine.av@gmail.com> - 0.0.14
- copy RPMS along with SRPMS
* Thu May 12 2016 Aditya Vaja <wolverine.av@gmail.com> - 0.0.13
- minor fix
* Thu May 12 2016 Aditya Vaja <wolverine.av@gmail.com> - 0.0.12
- add build infra to automate upload and rpm packaging
* Thu Apr 21 2016 Aditya Vaja <wolverine.av@gmail.com> - 2015.3.2
- Release 2015.3.2 with visual and navigation fixes
* Fri Apr 15 2016 Aditya Vaja <wolverine.av@gmail.com> - 2015.3.1
- Release 2015.2.1 package for liberty
* Fri Apr 15 2016 Aditya Vaja <wolverine.av@gmail.com> - 2015.2.1
- Release 2015.2.1 package for kilo_v2
* Sat Mar 5 2016 Xin Wu <xin.wu@bigswitch.com> - 0.0.1-1
- Initial rpm for horizon-rpm

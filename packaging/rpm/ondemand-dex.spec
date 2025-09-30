%{!?package_release: %define package_release 1}
%{!?package_version: %define package_version 2.41.1}

%define go_version 1.25.1
%ifarch x86_64
%define platform amd64
%endif
%ifarch aarch64
%define platform arm64
%endif
%ifarch ppc64le
%define platform ppc64le
%endif

%define debug_package %{nil}
%define __strip /bin/true

%define appname dex
%define confdir %{_sysconfdir}/ood/%{appname}

Name:       ondemand-%{appname}
Version:    %{package_version}
Release:    %{package_release}%{?dist}
Summary:    A federated OpenID Connect provider

Group:      System Environment/Daemons
License:    Apache-2.0
URL:        https://github.com/dexidp/dex
Source0:    https://github.com/OSC/ondemand-dex/archive/ondemand-dex-%{package_version}.tar.gz
Source1:    https://github.com/dexidp/dex/archive/v%{version}.tar.gz
Source2:    https://dl.google.com/go/go%{go_version}.linux-%{platform}.tar.gz
# Adds session support
# Original commit: https://github.com/juliantaylor/dex/commit/b3fc3e6c2295c0af166803bdde0977ed170d1d40
Source5:    https://github.com/OSC/dex/commit/6bb420ddb82613edce6e8b24a293da64006a5da3.patch

BuildRequires:  ondemand-scldevel
BuildRequires:  systemd
BuildRequires:  git
BuildRequires:  patch
Requires:       systemd
Requires:       %{?scl_ondemand_prefix_apache}mod_auth_openidc

%description
A federated OpenID Connect provider packaged for Open OnDemand

%prep
%setup -q -n ondemand-%{appname}-%{version}
%__tar -C %{_builddir} -xzf %{SOURCE1}
%__tar -C %{_builddir} -xzf %{SOURCE2}


%build
export PATH=$PATH:%{_builddir}/go/bin
cd %{_builddir}/%{appname}-%{version}
%__make build -j 4
%__mv bin/dex bin/dex-orig
%__patch -p1 < %{SOURCE5}
%__make build -j 4
%__mv bin/dex bin/dex-session
%__mv bin/dex-orig bin/dex


%install
%__install -p -m 755 -D %{_builddir}/%{appname}-%{version}/bin/dex %{buildroot}%{_sbindir}/%{name}
%__install -p -m 755 -D %{_builddir}/%{appname}-%{version}/bin/dex-session %{buildroot}%{_sbindir}/%{name}-session
%__install -p -m 600 -D %{_builddir}/%{appname}-%{version}/examples/config-dev.yaml %{buildroot}%{confdir}/config.yaml
touch %{buildroot}%{confdir}/dex.db
%__mkdir_p %{buildroot}%{_datadir}/%{name}
%__cp -R web %{buildroot}%{_datadir}/%{name}/web
%__mkdir_p %{buildroot}%{_sysconfdir}/systemd/system/%{name}.service.d
%__cat >> %{buildroot}%{_sysconfdir}/systemd/system/%{name}.service.d/session.conf.example << EOF
[Service]
ExecStart=
ExecStart=%{_sbindir}/%{name}-session serve %{confdir}/config.yaml
EOF
%__mkdir_p %{buildroot}%{_unitdir}
%__cat >> %{buildroot}%{_unitdir}/%{name}.service << EOF
[Unit]
Description=OnDemand Dex - A federated OpenID Connect provider packaged for OnDemand
After=network-online.target multi-user.target
Wants=network-online.target

[Service]
SyslogIdentifier=%{name}
WorkingDirectory=%{_datadir}/%{name}
ExecStart=%{_sbindir}/%{name} serve %{confdir}/config.yaml
User=%{name}
Group=%{name}

[Install]
WantedBy=multi-user.target
EOF

%clean
%__rm -rf %{_builddir}/go

%pre
getent group %{name} > /dev/null || groupadd -r %{name}
getent passwd %{name} > /dev/null || useradd -r -d /var/lib/%{name} -g %{name} -s /sbin/nologin -c "OnDemand Dex" %{name}

%post
%systemd_post %{name}.service
# On install, run update_ood_portal if installed
if [ $1 == 1 ]; then
  if [ -f /opt/ood/ood-portal-generator/sbin/update_ood_portal ]; then
    /opt/ood/ood-portal-generator/sbin/update_ood_portal --rpm
  fi
fi

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service

%files
%{_sbindir}/%{name}
%{_sbindir}/%{name}-session
%dir %attr(0700,%{name},%{name}) %{confdir}
%config(noreplace,missingok) %attr(0600,%{name},%{name}) %{confdir}/config.yaml
%ghost %{confdir}/dex.db
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/*
%dir %{_sysconfdir}/systemd/system/%{name}.service.d
%ghost %{_sysconfdir}/systemd/system/%{name}.service.d/session.conf
%{_sysconfdir}/systemd/system/%{name}.service.d/session.conf.example
%{_unitdir}/%{name}.service

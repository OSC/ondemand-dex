%{!?package_release: %define package_release 1}

%define go_version 1.14.2

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
Source0:    https://github.com/dexidp/dex/archive/v%{version}.tar.gz
Source1:    https://dl.google.com/go/go%{go_version}.linux-amd64.tar.gz
Source2:    theme.tar.gz
Source3:    templates.tar.gz
Source4:    static.tar.gz
# Adds session support
Source5:    https://github.com/OSC/dex/commit/b3fc3e6c2295c0af166803bdde0977ed170d1d40.patch

BuildRequires:  ondemand-scldevel
BuildRequires:  systemd
BuildRequires:  git
BuildRequires:  patch
Requires:       systemd
Requires:       %{?scl_ondemand_prefix_apache}mod_auth_openidc

%description
A federated OpenID Connect provider packaged for Open OnDemand

%prep
%setup -q -n %{appname}-%{version}
%__tar -C %{_buildrootdir} -xzf %{SOURCE1}
export PATH=$PATH:%{_buildrootdir}/go/bin
GOPATH=$(go env GOPATH)
%__mkdir_p $GOPATH/src/github.com/dexidp/dex
%__cp -R ./* $GOPATH/src/github.com/dexidp/dex/

%build
export PATH=$PATH:%{_buildrootdir}/go/bin
GOPATH=$(go env GOPATH)
cd $GOPATH/src/github.com/dexidp/dex/
%__make bin/dex
%__mv bin/dex bin/dex-orig
%__patch -p1 < %{SOURCE5}
%__make bin/dex
%__mv bin/dex bin/dex-session
%__mv bin/dex-orig bin/dex


%install
export PATH=$PATH:%{_buildrootdir}/go/bin
GOPATH=$(go env GOPATH)
cd $GOPATH/src/github.com/dexidp/dex/
%__install -p -m 755 -D bin/dex %{buildroot}%{_sbindir}/%{name}
%__install -p -m 755 -D bin/dex-session %{buildroot}%{_sbindir}/%{name}-session
%__install -p -m 600 -D examples/config-dev.yaml %{buildroot}%{confdir}/config.yaml
touch %{buildroot}%{confdir}/dex.db
%__mkdir_p %{buildroot}%{_datadir}/%{name}
%__cp -R web %{buildroot}%{_datadir}/%{name}/web
%__mkdir_p %{buildroot}%{_datadir}/%{name}/web/themes/ondemand
%__tar -C %{buildroot}%{_datadir}/%{name}/web/themes/ondemand -xzf %{SOURCE2}
%__tar -C %{buildroot}%{_datadir}/%{name}/web/templates -xzf %{SOURCE3}
%__tar -C %{buildroot}%{_datadir}/%{name}/web/static -xzf %{SOURCE4}
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
%__rm -rf %{_buildrootdir}/go

%pre
getent group %{name} > /dev/null || groupadd -r %{name}
getent passwd %{name} > /dev/null || useradd -r -d /var/lib/%{name} -g %{name} -s /sbin/nologin -c "OnDemand Dex" %{name}

%post
%systemd_post %{name}.service

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

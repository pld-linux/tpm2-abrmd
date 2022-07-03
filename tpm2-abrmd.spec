# TODO: handle selinux policy (--with-sepolicy)
#
# Conditional build:
%bcond_without	static_libs	# static library
%bcond_without	tests		# unit/emulated integration tests

Summary:	TPM2 Access Broker and Resource Management Daemon
Summary(pl.UTF-8):	Broker dostępu i demon zarządzający zasobami TPM2
Name:		tpm2-abrmd
Version:	2.4.1
Release:	1
License:	BSD
Group:		Libraries
#Source0Download: https://github.com/tpm2-software/tpm2-abrmd/releases
Source0:	https://github.com/tpm2-software/tpm2-abrmd/releases/download/%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	674881dc8a1385c28f9a6ea0585da259
URL:		https://github.com/tpm2-software/tpm2-abrmd
BuildRequires:	glib2-devel >= 2.0
BuildRequires:	pkgconfig
BuildRequires:	sed >= 4.0
BuildRequires:	tpm2-tss-devel >= 2.4.0
%if %{with tests}
BuildRequires:	cmocka-devel >= 1.0
# ss (real iproute2 package required, not the false one provided by vserver-packages)
BuildRequires:	/sbin/ss
BuildRequires:	iproute2
# or ibmswtpm2
BuildRequires:	swtpm
%endif
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
This is a system daemon implementing the TPM2 access broker (TAB) &
Resource Manager (RM) spec from the TCG. The daemon (tpm2-abrmd) is
implemented using GLib and the GObject system.

%description -l pl.UTF-8
Ten pakiet zawiera demona będącego implementacją spefycikacji
brokera dostępowego TPM2 (TAB) oraz zarządcy zasobów (RM) pochodzących
z TCG. Demon jest zaimplementowany przy użyciu bibliotek GLib i
GObject.

%package devel
Summary:	Header files for tpm2-abrmd library
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki tpm2-abrmd
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	glib2-devel >= 2.0
Requires:	tpm2-tss-devel

%description devel
Header files for tpm2-abrmd library.

%description devel -l pl.UTF-8
Pliki nagłówkowe biblioteki tpm2-abrmd.

%package static
Summary:	Static tpm2-abrmd library
Summary(pl.UTF-8):	Statyczna biblioteka tpm2-abrmd
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
Static tpm2-abrmd library.

%description static -l pl.UTF-8
Statyczna biblioteka tpm2-abrmd.

%prep
%setup -q

# set VERSION properly when there is no .git directory
%{__sed} -i -e 's/m4_esyscmd_s(\[git describe --tags --always --dirty\])/%{version}/' configure.ac

%build
%{__libtoolize}
%{__aclocal} -I m4
%{__autoconf}
%{__automake}
# PATH for /sbin/ss
export PATH=${PATH:+$PATH:}/sbin
%configure \
	%{?with_tests:--enable-integration} \
	--disable-silent-rules \
	%{!?with_static_libs:--disable-static-libs} \
	%{?with_tests:--enable-unit} \
	--with-dbuspolicydir=%{_datadir}/dbus-1/system.d \
	--with-systemdpresetdir=/lib/systemd/system-preset \
	--with-systemdsystemunitdir=%{systemdunitdir}

%{__make}

%if %{with tests}
%{__make} check
%endif

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

# obsoleted by pkg-config
%{__rm} $RPM_BUILD_ROOT%{_libdir}/libtss2-tcti-tabrmd.la

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc AUTHORS CHANGELOG.md LICENSE README.md
%attr(755,root,root) %{_sbindir}/tpm2-abrmd
%attr(755,root,root) %{_libdir}/libtss2-tcti-tabrmd.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libtss2-tcti-tabrmd.so.0
%{_datadir}/dbus-1/system-services/com.intel.tss2.Tabrmd.service
%{_datadir}/dbus-1/system.d/tpm2-abrmd.conf
/lib/systemd/system-preset
%{systemdunitdir}/tpm2-abrmd.service
%{_mandir}/man8/tpm2-abrmd.8*

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libtss2-tcti-tabrmd.so
%{_includedir}/tss2/tss2-tcti-tabrmd.h
%{_pkgconfigdir}/tss2-tcti-tabrmd.pc
%{_mandir}/man3/Tss2_Tcti_Tabrmd_Init.3*
%{_mandir}/man7/tss2-tcti-tabrmd.7*

%if %{with static_libs}
%files static
%defattr(644,root,root,755)
%{_libdir}/libtss2-tcti-tabrmd.a
%endif

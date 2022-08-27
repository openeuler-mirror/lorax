%define debug_package %{nil}
%define disable_cross 0

Name:           lorax
Version:        33.6
Release:        3
Summary:        A set of tools used to create bootable images
License:        GPLv2+
URL:            https://github.com/weldr/lorax
Source0:        https://github.com/weldr/lorax/archive/%{name}-%{version}-1.tar.gz

Patch0:		0001-ignore-the-dir-that-without-kernel-version.patch
Patch1:		0001-add-text-mode-selection-menu-in-grub-configuration.patch
Patch2:		0001-use-tty0-other-than-ttyAMA0-in-rescue-mode.patch
Patch3:		0001-delete-kernel-modules-pkg.patch
Patch4:		0001-disable-isolabel-character-change.patch
Patch5:		disable-graphics-install.patch
Patch6:		disable-GeoIP.patch
Patch7:		eliminate-difference.patch
Patch8:		lorax-enable-GUI-installation.patch
Patch9:		lorax-enable-anaconda-KdumpSpoke.patch
Patch10:	lorax-delete-udisk2-iscsi.patch
Patch11:	backport-Do-not-use-loglevel-option-when-running-Anaconda.patch
Patch12:	backport-Improve-lmc-no-virt-error-handling.patch
Patch13:	backport-Add-POSTIN-scriptlet-error-to-the-log-monitor-list.patch
Patch14:	backport-Remove-LD_PRELOAD-libgomp.so.1-from-lmc-no-virt.patch

BuildRequires:  python3-devel python3-sphinx_rtd_theme python3-magic 
BuildRequires:  python3-nose python3-pytest-mock python3-pocketlint python3-gevent
BuildRequires:  python3-mock python3-urllib3 python3-dnf python3-librepo 
BuildRequires:  python3-libselinux python3-mako python3-kickstart

Requires:       lorax-templates GConf2 cpio device-mapper dosfstools e2fsprogs
Requires:       findutils gawk xorriso glib2 glibc glibc-common gzip isomd5sum
Requires:       module-init-tools parted squashfs-tools util-linux xz-lzma-compat xz pigz
Requires:       pbzip2 dracut kpartx libselinux-python3 python3-mako python3-kickstart
Requires:       python3-dnf python3-librepo python3-pycdlib
      
%ifarch %{ix86} x86_64
Requires:       syslinux >= 6.03-1
Requires:       syslinux-nonlinux >= 6.03-1
%endif

%ifarch %{arm}
Requires:       uboot-tools
%endif

Provides:       appliance-tools-minimizer = %{version}-%{release}
Obsoletes:      appliance-tools-minimizer < 007.7-3
Provides:       lorax-templates-generic = %{version}-%{release}
Obsoletes:      lorax-templates-generic < %{version}-%{release}
Provides:       lorax-templates = %{version}-%{release}

%description
Tools for creating images, including the Anaconda boot.iso, live disk images, iso's,
and filesystem images.

It also includes livemedia-creator which is used to create bootable livemedia,
including live isos and disk images. It can use libvirtd for the install, or
Anaconda's image install feature.

The package including lorax-templates-generic
lorax-templates-generic,Generic build templates for lorax and livemedia-creator

%if 0%{?disable_cross}
%package       lmc-virt
Summary:       livemedia-creator libvirt dependencies
Requires:      lorax = %{version}-%{release} qemu edk2-ovmf
Recommends:    qemu-kvm

%description   lmc-virt
Additional dependencies required by livemedia-creator when using it with qemu.
%endif

%package       lmc-novirt
Summary:       livemedia-creator no-virt dependencies
Requires:      lorax = %{version}-%{release} anaconda-core anaconda-tui system-logos

%description   lmc-novirt
Additional dependencies required by livemedia-creator when using it with --no-virt
to run Anaconda.

%package       composer
Summary:       Lorax Image Composer API Server
BuildRequires: python3-flask python3-gobject libgit2-glib python3-pytoml python3-semantic_version

Requires:      lorax = %{version}-%{release}
Requires(pre): /usr/bin/getent /usr/sbin/groupadd /usr/sbin/useradd

Requires:      python3-toml  python3-semantic_version libgit2 libgit2-glib
Requires:      python3-flask python3-gevent anaconda-tui qemu-img tar

%{?systemd_requires}
BuildRequires: systemd

%description   composer
lorax-composer provides a REST API for building images using lorax.

%package -n    composer-cli
Summary: A command line tool for use with the lorax-composer API server

Requires:      python3-urllib3

%description -n composer-cli
A command line tool for use with the lorax-composer API server. Examine recipes,
build images, etc. from the command line.

%package_help

%prep
%setup -q -n %{name}-%{name}-%{version}-1
%patch0 -p1
%ifarch aarch64
%patch1 -p1
%patch2 -p1
%endif
%patch3 -p1

%patch4 -p1
%ifarch aarch64
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1
%patch10 -p1
%endif
%patch11 -p1
%patch12 -p1
%patch13 -p1
%patch14 -p1
%build
%make_build

%install
%make_install DESTDIR=%{buildroot} mandir=%{_mandir} 
install -dp %{buildroot}/var/lib/lorax/composer/blueprints/
for toml in example-http-server.toml example-development.toml example-atlas.toml; do
    cp ./tests/pylorax/blueprints/$toml %{buildroot}/var/lib/lorax/composer/blueprints/
done


%pre composer
getent group weldr >/dev/null 2>&1 || groupadd -r weldr >/dev/null 2>&1 || :
getent passwd weldr >/dev/null 2>&1 || useradd -r -g weldr -d / -s /sbin/nologin -c "User for lorax-composer" weldr >/dev/null 2>&1 || :

%post composer
%systemd_post lorax-composer.service
%systemd_post lorax-composer.socket

%preun composer
%systemd_preun lorax-composer.service
%systemd_preun lorax-composer.socket

%postun composer
%systemd_postun_with_restart lorax-composer.service
%systemd_postun_with_restart lorax-composer.socket

%files
%defattr(-,root,root,-)
%doc AUTHORS docs/livemedia-creator.rst docs/product-images.rst
%doc docs/*ks ANNOUNCE POLICY
%license COPYING
%config(noreplace) %{_sysconfdir}/lorax/lorax.conf
%{python3_sitelib}/pylorax
%{python3_sitelib}/*.egg-info
%{_bindir}/image-minimizer
%{_bindir}/mk-s390-cdboot
%{_sbindir}/lorax
%{_sbindir}/mkefiboot
%{_sbindir}/livemedia-creator
%{_sbindir}/mkksiso
%dir %{_sysconfdir}/lorax
%dir %{_datadir}/lorax
%dir %{_datadir}/lorax/templates.d
%{_datadir}/lorax/templates.d/*
%{_tmpfilesdir}/lorax.conf

%if 0%{?disable_cross}
%files lmc-virt
%endif

%files lmc-novirt

%files composer
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/lorax/composer.conf
%{python3_sitelib}/pylorax/api/*
%{python3_sitelib}/lifted/*
%{_sbindir}/lorax-composer
%{_unitdir}/lorax-composer.*
%dir %{_datadir}/lorax/composer
%{_datadir}/lorax/composer/*
%{_datadir}/lorax/lifted/*
%{_tmpfilesdir}/lorax-composer.conf
%dir %attr(0771, root, weldr) %{_sharedstatedir}/lorax/composer/
%dir %attr(0771, root, weldr) %{_sharedstatedir}/lorax/composer/blueprints/
%attr(0771, weldr, weldr) %{_sharedstatedir}/lorax/composer/blueprints/*

%files -n composer-cli
%defattr(-,root,root,-)
%{_sysconfdir}/bash_completion.d/composer-cli
%{_bindir}/composer-cli
%{python3_sitelib}/composer/*

%files help
%defattr(-,root,root)
%doc HACKING.md README.md
%{_mandir}/man1/*.1*

%changelog
* Mon Apr 12 2021 orange-snn <songnannan2@huawei.com> - 33.6-3
- add python3-pycdlib in requires for livecd

* Tue Mar 30 2021 yuboyun <yuboyun@huawei.com> - 33.6-2
- Do not use '--loglevel' option when running Anaconda
  Improve Imc no-virt error handling
  Add POSTIN scriptlet error to the log monitor list
  Remove LD_PRELOAD libgomp.so.1 from Imc --no-virt

* Wed Oct 28 2020 zhangqiumiao <zhangqiumiao1@huawei.com> - 33.6-1
- upgrade to 33.6

* Mon May 25 2020 songnannan <songnannan2@huawei.com> - 29.16-11
- rebuild for the update packages

* Mon Mar 16 2020 songnannan <songnannan2@huawei.com> - 29.16-10
- disbale the virt pacakge

* Mon Feb 24 2020 openEuler Buildteam <buildteam@openeuler.org> - 29.16-9
- Type:bugfix
- Id:NA
- SUG:NA
- DESC:Fix live-iso creation on aarch64

* Thu Jan 16 2020 openEuler Buildteam <buildteam@openeuler.org> - 29.16-8
- Type:bugfix
- Id:NA
- SUG:NA
- DESC:delete udisk2-iscsi

* Wed Jan 15 2020 openEuler Buildteam <buildteam@openeuler.org> - 29.16-7
- Type:bugfix
- Id:NA
- SUG:NA
- DESC:fix selfbuild error

* Tue Dec 31 2019 openEuler Buildteam <buildteam@openeuler.org> - 29.16-6
- Type:bugfix
- Id:NA
- SUG:NA
- DESC:optimization the spec

* Mon Oct 21 2019 openEuler Buildteam <buildteam@openeuler.org> - 29.16-5
- Type:bugfix
- Id:NA
- SUG:NA
- DESC: add lorax-lmc-virt package

* Fri Oct 11 2019 openEuler Buildteam <buildteam@openeuler.org> - 29.16-4
- spec modify

* Fri Aug 23 2019 cangyi<cangyi@huawei.com> - 29.16-3
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:format patches

* Fri Aug 16 2019 fanghuiyu<fanghuiyu@huawei.com> - 29.16-2
- Type:enhancement
- ID:NA
- SUG:NA
- DESC:enable GUI installation

* Wed Jul 3 2019 zhujunhao<zhujunhao5@huawei.com> - 29.16-1.h7
- Type:enhancement
- ID:NA
- SUG:NA
- DESC:eliminate-difference

* Thu Mar 28 2019 tianhang<tianhang1@huawei.com> - 29.16-1.h6
- Type:enhancement
- ID:NA
- SUG:NA
- DESC:disable GeoIP for anaconda

* Wed Feb 27 2019 hexiaowen<hexiaowen@huawei.com> - 29.16-1.h5
- Type:enhancement
- ID:NA
- SUG:NA
- DESC:disable graphic install and add console cmdline

* Wed Feb 27 2019 hexiaowen<hexiaowen@huawei.com> - 29.16-1.h4
- Type:enhancement
- ID:NA
- SUG:NA
- DESC:disable graphic install

* Fri Jan 11 2019 zhouyihang<zhouyihang1@huawei.com> - 29.16-1.h3
- Type:enhancement
- ID:NA
- SUG:NA
- DESC:disable isolabel character change

* Thu Jan 10 2019 liuxueping<liuxueping1@huawei.com> - 29.16-1.h2
- Type:enhancement
- ID:NA
- SUG:NA
- DESC:delete kernel-modules pkgs

* Sat Dec 29 2018 liuxueping<liuxueping1@huawei.com> - 29.16-1.h1
- Type:enhancement
- ID:NA
- SUG:NA
- DESC:use tty0 rather than ttyAMA0 for rescue mode on aarch64 machine
       ignore the dir that without kernel version
       add text mode in aarch64 installation



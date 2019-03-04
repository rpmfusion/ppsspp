# https://github.com/hrydgard/ppsspp/issues/8823
ExcludeArch: %{power64}

# -Wl,--as-needed breaks linking on fedora 30+ 
%undefine _ld_as_needed

%global commit 74d87fa2b4a3c943c1df09cc26a8c70b1335fd30
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global date 20181204

Name:           ppsspp
Version:        1.7.5
Release:        2%{?dist}
Summary:        A PSP emulator
License:        BSD and GPLv2+
URL:            https://www.ppsspp.org/

## This commit coincides with the commit of release 1.7.4
## We need to checkout it, then download relative submodules
## which are not included in the source code:
##
# git clone https://github.com/hrydgard/ppsspp.git
# git checkout %%{commit}
# git submodule update --init ext/armips
# git submodule update --init ext/glslang
# git submodule update --init ext/SPIRV-Cross
# git submodule update --init ext/discord-rpc
# rm -rf ppsspp/.git ppsspp/.gitignore
# tar -czvf ppsspp-%%{version}.tar.gz ppsspp
##
Source0:        ppsspp-%{version}.tar.gz
Source1:        %{name}.desktop
Source2:        %{name}.appdata.xml

# Fix version
Patch0:         %{name}-1.1.0-git-version.patch
Patch1:         %{name}-armv7.patch

# https://github.com/hrydgard/ppsspp/pull/11507
Patch2:         %{name}-1.7.0-upstream_bug11507.patch

BuildRequires:  mesa-libEGL-devel
BuildRequires:  mesa-libGLES-devel
BuildRequires:  cmake3
BuildRequires:  chrpath
BuildRequires:  desktop-file-utils
BuildRequires:  ffmpeg-devel
BuildRequires:  wayland-devel
BuildRequires:  snappy-devel
BuildRequires:  SDL2-devel
BuildRequires:  gcc, gcc-c++
BuildRequires:  libzip-devel
BuildRequires:  zlib-devel
BuildRequires:  glew-devel
BuildRequires:  libGL-devel
BuildRequires:  qt5-qtbase-devel
BuildRequires:  qt5-qttools-devel
BuildRequires:  libappstream-glib
BuildRequires:  rapidjson-devel

Requires: %{name}-data = %{version}-%{release}
Requires: hicolor-icon-theme

%description
PPSSPP - a fast and portable PSP emulator.


%package data
Summary: Data files of %{name}
BuildArch: noarch

%description data
Data files of %{name}.


%prep
%autosetup -n %{name} -p1

# Set version
sed -e 's|@@unknown_version@@|%{version}|g' -i git-version.cmake

# Remove unrecognized flag
sed -i.bak '/Wno-deprecated-register/d' CMakeLists.txt

# Downgrade optimization level to the default one for fedora
sed -e 's| -O3 | -O2 |g' -i CMakeLists.txt

## Remove spurious executable permissions
find ext Core -perm /755 -type f \( -name "*.cpp" -o -name "*.h" -o -name "*.hpp" -o -name "*.y" \) -exec  chmod -x {} ';'


%build
export LDFLAGS="%{__global_ldflags} -lGL -fPIC"
%cmake3 -DCMAKE_BUILD_TYPE:STRING=Release \
 -DCMAKE_INSTALL_LIBDIR:PATH=%{_lib}/%{name} \
 -Wno-dev -DARMIPS_REGEXP:BOOL=OFF \
 -DCMAKE_VERBOSE_MAKEFILE:BOOL=TRUE \
 -DUSE_FFMPEG:BOOL=ON -DUSE_SYSTEM_FFMPEG:BOOL=ON \
 -DUSE_SYSTEM_LIBZIP:BOOL=ON -DUSE_WAYLAND_WSI:BOOL=ON \
 -DUSING_EGL:BOOL=ON -DUSING_GLES2:BOOL=ON -DUSING_X11_VULKAN=ON \
 -DUSING_QT_UI:BOOL=ON -DENABLE_GLSLANG_BINARIES:BOOL=OFF \
 -DLIBRETRO:BOOL=ON -DENABLE_HLSL:BOOL=OFF \
 -DOPENGL_xmesa_INCLUDE_DIR:PATH="%{_includedir}/GL -I%{_includedir}/GLES2" \
 -DHEADLESS=OFF -DZLIB_INCLUDE_DIR:PATH=%{_includedir} \
%ifarch %{ix86}
 -DX86:BOOL=ON \
%endif
%ifarch %{arm} aarch64
 -DARM:BOOL=ON \
%endif
%ifarch armv7l armv7hl armv7hnl
 -DARMV7:BOOL=ON \
%endif
%ifarch x86_64
 -DX86_64:BOOL=ON \
%endif
 -DBUILD_TESTING:BOOL=OFF
%make_build V=1


%install
%make_install

# Install PPSSPP executable
install -Dpm 755 ./PPSSPPQt %{buildroot}%{_bindir}/PPSSPPQt

# Set rpath
chrpath -r %{_libdir}/%{name} %{buildroot}%{_bindir}/PPSSPPQt

# Install data files
mkdir -p %{buildroot}%{_datadir}/%{name}
cp -a ./assets %{buildroot}%{_datadir}/%{name}/
install -pm 644 Qt/languages/* %{buildroot}%{_datadir}/%{name}/assets/lang/

# Remove unnecessary files
rm -rf %{buildroot}%{_includedir}

# Install icons
mkdir -p %{buildroot}%{_datadir}/icons
cp -a icons/hicolor %{buildroot}%{_datadir}/icons/

mkdir -p %{buildroot}%{_datadir}/icons/%{name}
install -pm 644 icons/icon-114.png %{buildroot}%{_datadir}/icons/%{name}/%{name}.png

# Install desktop file
mkdir -p %{buildroot}%{_datadir}/applications
desktop-file-install -m 644 %SOURCE1 --dir=%{buildroot}%{_datadir}/applications

# Install appdata file
mkdir -p %{buildroot}%{_metainfodir}
install -pm 644 %SOURCE2 %{buildroot}%{_metainfodir}/
appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/*.appdata.xml

%if 0%{?rhel}
%post
/bin/touch --no-create %{_datadir}/icons/%{name} &>/dev/null || :

%postun
if [ $1 -eq 0 ] ; then
    /bin/touch --no-create %{_datadir}/icons/%{name} &>/dev/null
    /usr/bin/gtk-update-icon-cache %{_datadir}/icons/%{name} &>/dev/null || :
fi

%posttrans
/usr/bin/gtk-update-icon-cache %{_datadir}/icons/%{name} &>/dev/null || :
%endif


%files
%{_bindir}/PPSSPPQt
%{_datadir}/icons/hicolor/*/apps/%{name}.png
%{_datadir}/icons/%{name}/
%{_datadir}/applications/%{name}.desktop
%{_metainfodir}/%{name}.appdata.xml
%{_libdir}/%{name}/


%files data
%doc README.md
%license LICENSE.TXT
%{_datadir}/%{name}/


%changelog
* Mon Mar 04 2019 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 1.7.5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Tue Dec 11 2018 Antonio Trande <sagitter@fedoraproject.org> - 1.7.5-1
- Release 1.7.5

* Mon Dec 03 2018 Antonio Trande <sagitter@fedoraproject.org> - 1.7.4-1
- Release 1.7.4

* Fri Nov 02 2018 Antonio Trande <sagitter@fedoraproject.org> - 1.7.1-1
- Release 1.7.1
- Enable USING_GLES2 option

* Sun Oct 28 2018 Antonio Trande <sagitter@fedoraproject.org> - 1.7.0-2
- Patched for upstream bug 11507

* Sat Oct 27 2018 Antonio Trande <sagitter@fedoraproject.org> - 1.7.0-1
- Release 1.7.0

* Wed Sep 12 2018 Antonio Trande <sagitter@fedoraproject.org> - 1.6.3-4.20180912git6d0ed4a
- Enable USE_WAYLAND_WSI
- Install runtime libraries

* Tue Sep 11 2018 Antonio Trande <sagitter@fedoraproject.org> - 1.6.3-3
- Use different ARM compiler flags (-mfpu=neon -fomit-frame-pointer -ftree-vectorize -mvectorize-with-neon-quad -ffast-math -DARM_NEON)
- Enable Vulkan
- BR reorganized

* Sat Sep 08 2018 Antonio Trande <sagitter@fedoraproject.org> - 1.6.3-2
- Wayland on epel7 uses an unversioned libwayland-egl library

* Wed Sep 05 2018 Antonio Trande <sagitter@fedoraproject.org> - 1.6.3-1
- Initial package

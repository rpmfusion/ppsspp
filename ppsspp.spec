# https://github.com/hrydgard/ppsspp/issues/8823
ExcludeArch: %{power64}

# -Wl,--as-needed breaks linking on fedora 30+ 
%undefine _ld_as_needed

%global commit e3c9793cb3a68ec9f44371c7ebb45a0abed1ecca
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global date 20191016

%bcond_with debug

# Note:
# SDL version works disabling EGL support.
# Qt version works disabling both EGL and GLES2 support.
%bcond_without qt

# EGL/GLES2 support.
%bcond_with egles2

Name:           ppsspp
Version:        1.9.4
Release:        2%{?dist}
Summary:        A PSP emulator
License:        BSD and GPLv2+
URL:            https://www.ppsspp.org/

## This commit coincides with the commit of release %%{version}.
## We need to checkout it, then download relative submodules
## which are not included in the source code:
##
# git clone https://github.com/hrydgard/ppsspp.git
# cd ppsspp && git checkout %%{commit}
# git submodule update --init ext/armips
# git submodule update --init ext/glslang
# git submodule update --init ext/SPIRV-Cross
# git submodule update --init ext/discord-rpc
# git clone https://github.com/hrydgard/ppsspp-lang
# rm -rf ppsspp-lang/.git
# cd ..
# rm -rf ppsspp/.git ppsspp/.gitignore
# tar -czvf ppsspp-%%{version}.tar.gz ppsspp
##
Source0:        ppsspp-%{version}.tar.gz
Source1:        %{name}.desktop
Source2:        %{name}.appdata.xml

# Fix version
Patch0:         %{name}-1.1.0-git-version.patch

# https://github.com/hrydgard/ppsspp/pull/12593
Patch1:         %{name}-bug12593.patch

%if %{with egles2}
BuildRequires:  mesa-libEGL-devel
BuildRequires:  mesa-libGLES-devel
%endif
BuildRequires:  cmake3
BuildRequires:  chrpath
BuildRequires:  desktop-file-utils
BuildRequires:  ffmpeg-devel
BuildRequires:  wayland-devel
BuildRequires:  snappy-devel
BuildRequires:  SDL2-devel
BuildRequires:  gcc, gcc-c++
BuildRequires:  libzip-devel
BuildRequires:  libpng-devel
BuildRequires:  zlib-devel
BuildRequires:  glew-devel
BuildRequires:  libGL-devel
%if %{with qt}
BuildRequires:  qt5-qtbase-devel
BuildRequires:  qt5-qttools-devel
%endif
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

# Remove bundled libzip libraries
rm -rf /ext/native/ext/libzip

# Set version
sed -e 's|@@unknown_version@@|%{version}|g' -i git-version.cmake

# Remove unrecognized flag
sed -i.bak '/-Wno-deprecated-register/d' CMakeLists.txt

# Downgrade optimization level
%if %{with debug}
sed -e 's| -O3 | -O0 |g' -i CMakeLists.txt ext/SPIRV-Cross/Makefile Tools/pauth_tool/Makefile ext/armips/ext/tinyformat/Makefile
sed -e 's| -O2 | -O0 |g' -i CMakeLists.txt ext/SPIRV-Cross/Makefile Tools/pauth_tool/Makefile ext/armips/ext/tinyformat/Makefile
sed -e 's| -D_NDEBUG | -DDEBUG |g' -i CMakeLists.txt libretro/Makefile ext/SPIRV-Cross/Makefile
sed -e 's| -DNDEBUG | -DDEBUG |g' -i ext/SPIRV-Cross/Makefile
%else
sed -e 's| -O3 | -O2 |g' -i CMakeLists.txt ext/SPIRV-Cross/Makefile Tools/pauth_tool/Makefile ext/armips/ext/tinyformat/Makefile
%endif

## Remove spurious executable permissions
find ext Core -perm /755 -type f \( -name "*.cpp" -o -name "*.h" -o -name "*.hpp" -o -name "*.y" \) -exec  chmod -x {} ';'


%build
mkdir build && pushd build

export LDFLAGS="%{__global_ldflags} -lGL -fPIC"
export CC=gcc
export CXX=g++

%if %{with debug}
export CXXFLAGS="-O0 -g -fPIC"
export CFLAGS="-O0 -g -fPIC"
%cmake3 -DCMAKE_BUILD_TYPE:STRING=RelWithDebInfo -DCMAKE_C_FLAGS_RELWITHDEBINFO:STRING="-O0 -g -DDEBUG" -DCMAKE_CXX_FLAGS_RELWITHDEBINFO:STRING="-O0 -g -DDEBUG" \
%else
%cmake3 -DCMAKE_BUILD_TYPE:STRING=Release \
%endif
 -DCMAKE_INSTALL_LIBDIR:PATH=%{_lib}/%{name} \
 -Wno-dev -DARMIPS_REGEXP:BOOL=OFF \
 -DCMAKE_VERBOSE_MAKEFILE:BOOL=TRUE \
 -DUSE_FFMPEG:BOOL=ON -DUSE_SYSTEM_FFMPEG:BOOL=ON \
 -DUSE_SYSTEM_LIBZIP:BOOL=ON -DUSE_WAYLAND_WSI:BOOL=ON \
%if %{with egles2}
 -DUSING_EGL:BOOL=OFF -DUSING_GLES2:BOOL=OFF \
 -DOPENGL_EGL_INCLUDE_DIR:PATH="%{_includedir}/EGL -I%{_includedir}/GLES2" \
%endif
 -DUSING_X11_VULKAN=ON \
 -DENABLE_GLSLANG_BINARIES:BOOL=OFF \
 -DLIBRETRO:BOOL=ON -DENABLE_HLSL:BOOL=OFF \
 -DOPENGL_xmesa_INCLUDE_DIR:PATH="%{_includedir}/GL" \
 -DHEADLESS=OFF -DZLIB_INCLUDE_DIR:PATH=%{_includedir} \
%if %{with qt}
 -DUSING_QT_UI:BOOL=ON \
 -DPNG_PNG_INCLUDE_DIR:PATH=%{_includedir}/libpng16 -DPNG_LIBRARY:FILEPATH=%{_libdir}/libpng.so \
%else
 -DUSING_QT_UI:BOOL=OFF \
 -DPNG_PNG_INCLUDE_DIR:PATH=../ext/native/ext/libpng17 \
%endif
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
 -DBUILD_TESTING:BOOL=OFF ..

%make_build V=1

popd

%install
%make_install -C build

# Install PPSSPP executable
%if %{with qt}
install -Dpm 755 build/PPSSPPQt %{buildroot}%{_bindir}/PPSSPPQt
%else
install -Dpm 755 build/PPSSPPSDL %{buildroot}%{_bindir}/PPSSPPSDL
%endif

# Set rpath
chrpath -r %{_libdir}/%{name} %{buildroot}%{_bindir}/PPSSPP*

# Install data files
mkdir -p %{buildroot}%{_datadir}/%{name}
cp -a build/assets %{buildroot}%{_datadir}/%{name}/

install -pm 644 ppsspp-lang/*.ini %{buildroot}%{_datadir}/%{name}/assets/lang/
install -pm 644 korean.txt %{buildroot}%{_datadir}/%{name}/assets/lang/korean.ini
install -pm 644 chinese.txt %{buildroot}%{_datadir}/%{name}/assets/lang/chinese.ini

# Remove unnecessary files
rm -rf %{buildroot}%{_includedir}

# Install icons
mkdir -p %{buildroot}%{_datadir}/icons/%{name}
cp -a icons/hicolor %{buildroot}%{_datadir}/icons/
install -pm 644 icons/icon-114.png %{buildroot}%{_datadir}/icons/%{name}/%{name}.png

# Install desktop file
mkdir -p %{buildroot}%{_datadir}/applications
desktop-file-install -m 644 %SOURCE1 --dir=%{buildroot}%{_datadir}/applications
%if %{with qt}
desktop-file-edit --set-key=Exec --set-value=%{_bindir}/PPSSPPQt %{buildroot}%{_datadir}/applications/ppsspp.desktop
%endif

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
%{_bindir}/PPSSPP*
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
* Wed Feb 19 2020 Antonio Trande <sagitter@fedoraproject.org> - 1.9.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild
- Patched for GCC-10

* Wed Nov 06 2019 Antonio Trande <sagitter@fedoraproject.org> - 1.9.4-2
- Unset EGL/GLES support

* Thu Oct 31 2019 Antonio Trande <sagitter@fedoraproject.org> - 1.9.4-1
- Release 1.9.4

* Thu Sep 26 2019 Antonio Trande <sagitter@fedoraproject.org> - 1.9.0-1
- Release 1.9.0

* Wed Aug 07 2019 Leigh Scott <leigh123linux@gmail.com> - 1.8.0-2
- Rebuild for new ffmpeg version

* Thu Mar 14 2019 Antonio Trande <sagitter@fedoraproject.org> - 1.8.0-1
- Release 1.8.0
- Install language .ini files
- Modify screenshot's links of the appdata file

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

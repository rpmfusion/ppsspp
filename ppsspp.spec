# https://github.com/hrydgard/ppsspp/issues/8823
ExcludeArch: %{power64}

# Disable LTO flags
# ... during IPA pass: pure-const
# lto1: internal compiler error: Segmentation fault
%define _lto_cflags %{nil}

%if 0%{?el7}
%global dts devtoolset-9-
%endif

# -Wl,--as-needed breaks linking on fedora 30+ 
%undefine _ld_as_needed

%global commit 087de849bdc74205dd00d8e6e11ba17a591213ab
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global date 20200712

%bcond_with debug

%global common_build_options \\\
 -DCMAKE_INSTALL_LIBDIR:PATH=%{_lib}/%{name} \\\
 -DPYTHON_EXECUTABLE:FILEPATH=%{__python3} \\\
 -Wno-dev -DARMIPS_REGEXP:BOOL=OFF \\\
 -DCMAKE_VERBOSE_MAKEFILE:BOOL=TRUE \\\
 -DUSE_FFMPEG:BOOL=ON -DUSE_SYSTEM_FFMPEG:BOOL=ON \\\
 -DUSE_SYSTEM_LIBZIP:BOOL=ON \\\
 -DUSE_SYSTEM_SNAPPY:BOOL=ON \\\
 %ifarch %{ix86} \
 -DX86:BOOL=ON \\\
 %endif \
 %ifarch %{arm} aarch64 \
 -DARM:BOOL=ON \\\
 %endif \
 %ifarch armv7l armv7hl armv7hnl \
 -DARMV7:BOOL=ON \\\
 %endif \
 %ifarch x86_64 \
 -DX86_64:BOOL=ON \\\
 %endif \
 -DBUILD_TESTING:BOOL=OFF \\\
 -DENABLE_GLSLANG_BINARIES:BOOL=OFF \\\
 -DENABLE_HLSL:BOOL=OFF \\\
 -DOPENGL_xmesa_INCLUDE_DIR:PATH= \\\
 -DHEADLESS=OFF -DZLIB_INCLUDE_DIR:PATH=%{_includedir}
 
 
Name:           ppsspp
Version:        1.10.3
Release:        5%{?dist}
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
Source3:        %{name}-qt.desktop
Source4:        %{name}-qt.appdata.xml

# See https://github.com/hrydgard/ppsspp/issues/13119
Source5:        %{name}-qt-wayland.desktop

# Fix version
Patch0: %{name}-1.1.0-git-version.patch
Patch1: %{name}-1.10.0-remove_unrecognized_flag.patch

BuildRequires:  pkgconfig(egl)
BuildRequires:  pkgconfig(glesv2)
%if 0%{?fedora} && 0%{?fedora} > 31
BuildRequires: pkgconfig(opengl)
%endif
%if 0%{?fedora} && 0%{?fedora} < 32
BuildRequires: pkgconfig(libglvnd)
%endif
%{?fedora:BuildRequires: pkgconfig(libpng)}
%{?el7:BuildRequires: libglvnd-devel}
%{?el7:BuildRequires: pkgconfig(libpng)}
%{?el8:BuildRequires: pkgconfig(libpng16)}
BuildRequires:  pkgconfig(glew)
BuildRequires:  cmake3
BuildRequires:  python%{python3_pkgversion}-devel
BuildRequires:  python%{python3_pkgversion}-setuptools
BuildRequires:  chrpath
BuildRequires:  desktop-file-utils
BuildRequires:  ffmpeg-devel
BuildRequires:  wayland-devel
BuildRequires:  snappy-devel
BuildRequires:  SDL2-devel
BuildRequires:  %{?dts}gcc, %{?dts}gcc-c++
BuildRequires:  libzip-devel
BuildRequires:  snappy-devel
BuildRequires:  zlib-devel
BuildRequires:  qt5-qtbase-devel
BuildRequires:  qt5-qttools-devel
BuildRequires:  qt5-qtmultimedia-devel
BuildRequires:  libappstream-glib
BuildRequires:  rapidjson-devel

%description
PPSSPP - a fast and portable PSP emulator.


%package data
Summary: Data files of %{name}
BuildArch: noarch
Requires: hicolor-icon-theme
%description data
Data files of %{name}.

%package libs
Summary: PPSSPP private libraries
%description libs
Private libraries used by PPSSPP.

%package sdl
Summary: PPSSPP with SDL frontend
Requires: %{name}-data = %{version}-%{release}
Requires: %{name}-libs%{?_isa} = %{version}-%{release}
Obsoletes: %{name} < 0:1.10.2
Provides: %{name} = 0:%{version}-%{release}
%description sdl
PPSSPP with SDL frontend.

%package qt
Summary: PPSSPP with Qt5 frontend wrapper
Requires: %{name}-data = %{version}-%{release}
Requires: %{name}-libs%{?_isa} = %{version}-%{release}
Obsoletes: %{name} < 0:1.10.2
%description qt
PPSSPP with Qt5 frontend wrapper.


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
mkdir -p build

export LDFLAGS="%{__global_ldflags} -fPIC"
export CC=gcc
export CXX=g++

%if 0%{?el7}
%{?dts:source /opt/rh/devtoolset-9/enable}
%endif

%if %{with debug}
export CXXFLAGS="-O0 -g -fPIC"
export CFLAGS="-O0 -g -fPIC"
%cmake3 -B build -DCMAKE_BUILD_TYPE:STRING=RelWithDebInfo -DCMAKE_C_FLAGS_RELWITHDEBINFO:STRING="-O0 -g -DDEBUG" -DCMAKE_CXX_FLAGS_RELWITHDEBINFO:STRING="-O0 -g -DDEBUG" \
%else
%cmake3 -B build -DCMAKE_BUILD_TYPE:STRING=Release \
%endif
 -DOpenGL_GL_PREFERENCE:STRING=GLVND \
 -DUSING_EGL:BOOL=OFF \
 -DUSING_GLES2:BOOL=OFF \
 -DUSING_X11_VULKAN:BOOL=ON \
 -DUSE_WAYLAND_WSI:BOOL=ON \
 -DLIBRETRO:BOOL=OFF \
 -DUSING_QT_UI:BOOL=OFF \
 %{common_build_options}
%make_build

mkdir -p build2
export LDFLAGS="%{__global_ldflags} -fPIC"
export CC=gcc
export CXX=g++

%if 0%{?el7}
%{?dts:source /opt/rh/devtoolset-9/enable}
%endif

%if %{with debug}
export CXXFLAGS="-O0 -g -fPIC"
export CFLAGS="-O0 -g -fPIC"
%cmake3 -B build2 -DCMAKE_BUILD_TYPE:STRING=RelWithDebInfo -DCMAKE_C_FLAGS_RELWITHDEBINFO:STRING="-O0 -g -DDEBUG" -DCMAKE_CXX_FLAGS_RELWITHDEBINFO:STRING="-O0 -g -DDEBUG" \
%else
%cmake3 -B build2 -DCMAKE_BUILD_TYPE:STRING=Release \
%endif
 -DOpenGL_GL_PREFERENCE:STRING=GLVND \
 -DUSING_EGL:BOOL=OFF \
 -DUSING_GLES2:BOOL=OFF \
 -DUSING_X11_VULKAN:BOOL=ON \
 -DUSE_WAYLAND_WSI:BOOL=ON \
 -DUSING_QT_UI:BOOL=ON \
 -DLIBRETRO:BOOL=ON \
 %{common_build_options}
%make_build

%install
%make_install -C build

# Install PPSSPP executable
mkdir -p %{buildroot}%{_bindir}
install -pm 755 build2/PPSSPPQt %{buildroot}%{_bindir}/
install -pm 755 build/PPSSPPSDL %{buildroot}%{_bindir}/

# Install libraries
mkdir -p %{buildroot}%{_libdir}/%{name}
cp -a build2/lib/*.a %{buildroot}%{_libdir}/%{name}/
cp -a build2/lib/*.so %{buildroot}%{_libdir}/%{name}/

cp -u build/lib/*.a %{buildroot}%{_libdir}/%{name}/
cp -u build/lib/*.so %{buildroot}%{_libdir}/%{name}/

# Fix rpaths
chrpath -r %{_libdir}/%{name} %{buildroot}%{_bindir}/PPSSPP*
chrpath -d %{buildroot}%{_libdir}/%{name}/*.so

# Install data files
mkdir -p %{buildroot}%{_datadir}/%{name}
cp -a build2/assets %{buildroot}%{_datadir}/%{name}/

install -pm 644 ppsspp-lang/*.ini %{buildroot}%{_datadir}/%{name}/assets/lang/
install -pm 644 Qt/languages/*.ts %{buildroot}%{_datadir}/%{name}/assets/lang/
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
desktop-file-install -m 644 %SOURCE3 --dir=%{buildroot}%{_datadir}/applications
desktop-file-install -m 644 %SOURCE5 --dir=%{buildroot}%{_datadir}/applications

# Install appdata file
mkdir -p %{buildroot}%{_metainfodir}
install -pm 644 %SOURCE2 %{buildroot}%{_metainfodir}/
install -pm 644 %SOURCE4 %{buildroot}%{_metainfodir}/
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

%files sdl
%doc README.md
%license LICENSE.TXT
%{_bindir}/PPSSPPSDL
%{_datadir}/applications/%{name}.desktop
%{_metainfodir}/%{name}.appdata.xml

%files qt
%doc README.md
%license LICENSE.TXT
%{_bindir}/PPSSPPQt
%{_datadir}/applications/%{name}-qt.desktop
%{_datadir}/applications/%{name}-qt-wayland.desktop
%{_metainfodir}/%{name}-qt.appdata.xml

%files libs
%doc README.md
%license LICENSE.TXT
%{_libdir}/%{name}/

%files data
%doc README.md
%license LICENSE.TXT
%{_datadir}/%{name}/
%{_datadir}/icons/hicolor/*/apps/%{name}.png
%{_datadir}/icons/%{name}/

%changelog
* Sun Dec 13 2020 Antonio Trande <sagitter@fedoraproject.org> - 1.10.3-5
- Fix CMake options

* Sat Sep 19 2020 Leigh Scott <leigh123linux@gmail.com> - 1.10.3-4
- Fix desktop files so appstream data is created

* Wed Aug 19 2020 Antonio Trande <sagitter@fedoraproject.org> - 1.10.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild
- Disable LTO flags

* Thu Jul 16 2020 Antonio Trande <sagitter@fedoraproject.org> - 1.10.3-2
- ppsspp-sdl now provides original previous ppsspp rpm

* Mon Jul 13 2020 Antonio Trande <sagitter@fedoraproject.org> - 1.10.3-1
- Release 1.10.3

* Sat Jul 11 2020 Antonio Trande <sagitter@fedoraproject.org> - 1.10.2-3
- Fix Fedora 31 builds

* Fri Jul 10 2020 Antonio Trande <sagitter@fedoraproject.org> - 1.10.2-2
- Fix EPEL7 builds

* Fri Jul 10 2020 Antonio Trande <sagitter@fedoraproject.org> - 1.10.2-1
- Release 1.10.2
- Create a Qt and a SDL version

* Sun Jun 28 2020 Antonio Trande <sagitter@fedoraproject.org> - 1.10.0-2
- BuildRequires python3-devel explicitly
- Use devtoolset-9 on EPEL7

* Sat Jun 27 2020 Antonio Trande <sagitter@fedoraproject.org> - 1.10.0-1
- Release 1.10.0

* Sat Feb 22 2020 RPM Fusion Release Engineering <leigh123linux@googlemail.com> - 1.9.4-4
- Rebuild for ffmpeg-4.3 git

* Wed Feb 19 2020 Antonio Trande <sagitter@fedoraproject.org> - 1.9.4-3
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

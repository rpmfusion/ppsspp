# https://github.com/hrydgard/ppsspp/issues/8823
ExcludeArch: %{power64}

%bcond_with qt

# Filter private libraries
%global __provides_exclude ^(%%(find %{buildroot}%{_libdir}/ppsspp -name '*.so' | xargs -n1 basename | sort -u | paste -s -d '|' -))
%global __requires_exclude ^(%%(find %{buildroot}%{_libdir}/ppsspp -name '*.so' | xargs -n1 basename | sort -u | paste -s -d '|' -))
#

# Disable LTO flags
# ... during IPA pass: pure-const
# lto1: internal compiler error: Segmentation fault
%define _lto_cflags %{nil}

# -Wl,--as-needed breaks linking
%undefine _ld_as_needed

# Use bundled FFMpeg
# See RPM Fusion bz#5889, and upstream bug #15308
%bcond_without ffmpeg

%ifarch x86_64
%global __arch x86_64
%endif
%ifarch %{arm}
%global __arch armv7
%endif
%ifarch aarch64
%global __arch aarch64
%endif

%global commit %{nil}
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global date %{nil}

%bcond_with debug

%global common_build_options \\\
 -DCMAKE_INSTALL_LIBDIR:PATH=%{_lib}/%{name} \\\
 -DPYTHON_EXECUTABLE:FILEPATH=%{__python3} \\\
 -Wno-dev -DARMIPS_REGEXP:BOOL=OFF \\\
 -DCMAKE_VERBOSE_MAKEFILE:BOOL=TRUE \\\
 -DUSE_FFMPEG:BOOL=ON \\\
%if %{with ffmpeg} \
 -DUSE_SYSTEM_FFMPEG:BOOL=OFF \\\
 -DFFmpeg_LIBRARY_avcodec:FILEPATH=${PWD}/ffmpeg/linux/%{__arch}/lib/libavcodec.so \\\
 -DFFmpeg_LIBRARY_avformat:FILEPATH=${PWD}/ffmpeg/linux/%{__arch}/lib/libavformat.so \\\
 -DFFmpeg_LIBRARY_avutil:FILEPATH=${PWD}/ffmpeg/linux/%{__arch}/lib/libavutil.so \\\
 -DFFmpeg_LIBRARY_swresample:FILEPATH=${PWD}/ffmpeg/linux/%{__arch}/lib/libswresample.so \\\
 -DFFmpeg_LIBRARY_swscale:FILEPATH=${PWD}/ffmpeg/linux/%{__arch}/lib/libswscale.so \\\
%else \
 -DUSE_SYSTEM_FFMPEG:BOOL=ON \\\
%endif \
 -DUSE_SYSTEM_LIBZIP:BOOL=ON \\\
 -DUSE_SYSTEM_SNAPPY:BOOL=ON \\\
 -DUSE_SYSTEM_MINIUPNPC:BOOL=ON \\\
 %ifarch %{ix86} \
 -DX86:BOOL=ON \\\
 %endif \
 %ifarch %{arm} aarch64 \
 -DARM:BOOL=ON \\\
 %endif \
 %ifarch %{arm} \
 -DARMV7:BOOL=ON \\\
 %endif \
 %ifarch x86_64 \
 -DX86_64:BOOL=ON \\\
 %endif \
 -DBUILD_SHARED_LIBS:BOOL=OFF \\\
 -DBUILD_TESTING:BOOL=OFF \\\
 -DENABLE_GLSLANG_BINARIES:BOOL=OFF \\\
 -DENABLE_HLSL:BOOL=OFF \\\
 -DOPENGL_xmesa_INCLUDE_DIR:PATH= \\\
 -DHEADLESS=OFF -DZLIB_INCLUDE_DIR:PATH=%{_includedir} \\\
 -DPNG_PNG_INCLUDE_DIR:PATH=%{_includedir}
 
 
Name:           ppsspp
Version:        1.19.2
Release:        1%{?dist}
Summary:        A PSP emulator
License:        BSD and GPLv2+
URL:            https://www.ppsspp.org/

# Source code archive is made by executing this Bash script
Source0:        %{name}-makesrc.sh

%if %{with ffmpeg}
Source1:        %{name}-ffmpeg-%{version}.tar.gz
%else
Source2:        %{name}-%{version}.tar.gz
%endif
Source3:        %{name}.desktop
Source4:        %{name}.appdata.xml
Source5:        %{name}-qt.desktop
Source6:        %{name}-qt.appdata.xml

# See https://github.com/hrydgard/ppsspp/issues/13119
Source7:        %{name}-qt-wayland.desktop

# Fix version
Patch0: %{name}-1.1.0-git-version.patch
Patch2: %{name}-ffmpeg-set_x64_build_flags.patch
Patch3: %{name}-ffmpeg-set_aarch64_build_flags.patch
Patch4: %{name}-ffmpeg-set_arm_build_flags.patch
Patch5: %{name}-1.18.1-fix_GCC15.patch

BuildRequires:  pkgconfig(egl)
BuildRequires:  pkgconfig(glesv2)
BuildRequires:  pkgconfig(opengl)
%{?fedora:BuildRequires: pkgconfig(libpng)}
%{?el7:BuildRequires: libglvnd-devel}
%{?el7:BuildRequires: pkgconfig(libpng)}
%{?el8:BuildRequires: pkgconfig(libpng16)}
BuildRequires:  cmake
BuildRequires:  make
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  patchelf
BuildRequires:  desktop-file-utils
%if %{without ffmpeg}
BuildRequires:  ffmpeg-devel
%endif
BuildRequires:  pkgconfig(glew)
BuildRequires:  pkgconfig(glu)
BuildRequires:  wayland-devel
BuildRequires:  snappy-devel
BuildRequires:  SDL2-devel
BuildRequires:  SDL2_ttf-devel
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  libzip-devel
Buildrequires:  miniupnpc-devel
BuildRequires:  snappy-devel
BuildRequires:  zlib-devel
%if %{with qt}
BuildRequires:  qt5-qtbase-devel
BuildRequires:  qt5-qttools-devel
BuildRequires:  qt5-qtmultimedia-devel
%endif
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
%if %{with ffmpeg}
License: GPLv3+ and LGPLv2+
Provides: bundled(ffmpeg) = 0:3.0.2
Provides: bundled(libavcodec) = 57
Provides: bundled(libavformat) = 57
Provides: bundled(libavutil) = 57
Provides: bundled(libswresample) = 2
Provides: bundled(libswscale) = 4
%endif
%description libs
Private libraries used by PPSSPP.

%if %{without qt}
%package sdl
Summary: PPSSPP with SDL frontend
Requires: %{name}-data = %{version}-%{release}
Requires: %{name}-libs%{?_isa} = %{version}-%{release}
Obsoletes: %{name}-qt < 0:%{version}-%{release}
%description sdl
PPSSPP with SDL frontend.
%endif

%if %{with qt}
%package qt
Summary: PPSSPP with Qt5 frontend wrapper
Requires: %{name}-data = %{version}-%{release}
Requires: %{name}-libs%{?_isa} = %{version}-%{release}
Obsoletes: %{name}-sdl < 0:%{version}-%{release}
%description qt
PPSSPP with Qt5 frontend wrapper.
%endif

%prep
%setup -qT -b 1 -n %{name}

%patch -P 0 -p1 -b .backup

%if %{with ffmpeg}
%patch -P 2 -p1 -b .backup
%patch -P 3 -p1 -b .backup
%patch -P 4 -p1 -b .backup
%endif

%patch -P 5 -p1 -b .backup

# Remove bundled libraries
rm -rf /ext/native/ext/libzip
rm -rf /ext/native/tools/prebuilt/win64
rm -rf /ext/rapidjson
rm -rf /ext/glew
rm -rf /ext/zlib
rm -rf /MoltenVK
%if %{without ffmpeg}
rm -rf ffmpeg
%endif

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
sed -e 's| -O3 | -O2 |g' -i CMakeLists.txt ext/SPIRV-Cross/Makefile ext/armips/ext/tinyformat/Makefile
%endif

## Remove spurious executable permissions
find ext Core -perm /755 -type f \( -name "*.cpp" -o -name "*.h" -o -name "*.hpp" -o -name "*.y" \) -exec  chmod -x {} ';'


%build

# Build bundled ffmpeg's shared libraries
# 'make install' command moves compiled libraries into linux/arch/lib directory
%if %{with ffmpeg}

# Remove pre-compiled ffmpeg static libraries
find ffmpeg -type f \( -name "*.a" \) -exec  rm -f {} ';'

pushd ffmpeg
export CFLAGS="%{optflags}"
export LDFLAGS="%{__global_ldflags}"

%ifarch x86_64
sh -x ./linux_x86-64.sh
%make_build
make install
%endif

%ifarch aarch64
sh -x ./linux_arm64.sh
%make_build
make install
%endif

%ifarch %{arm}
sh -x ./linux_arm.sh
%make_build
make install
%endif
popd
%endif
#

mkdir -p build
%if %{with debug}
export CXXFLAGS="-O0 -g -lEGL -lGLESv2"
export CFLAGS="-O0 -g -lEGL -lGLESv2"
%cmake -B build -DCMAKE_BUILD_TYPE:STRING=RelWithDebInfo \
 -DCMAKE_C_FLAGS_RELWITHDEBINFO:STRING="-O0 -g -DDEBUG" \
 -DCMAKE_CXX_FLAGS_RELWITHDEBINFO:STRING="-O0 -g -DDEBUG" \
%else
export CXXFLAGS="%{build_cxxflags} -lEGL -lGLESv2"
export CFLAGS="%{build_cflags} -lEGL -lGLESv2"
%cmake -B build -DCMAKE_BUILD_TYPE:STRING=Release \
 -DCMAKE_C_FLAGS_RELEASE:STRING="%{build_cxxflags} -lEGL -lGLESv2" \
 -DCMAKE_CXX_FLAGS_RELEASE:STRING="%{build_cflags} -lEGL -lGLESv2" \
%endif
 -DOpenGL_GL_PREFERENCE:STRING=GLVND \
 -DUSING_EGL:BOOL=ON \
 -DUSING_GLES2:BOOL=ON \
 -DUSING_X11_VULKAN:BOOL=ON \
 -DUSE_VULKAN_DISPLAY_KHR:BOOL=ON \
 -DUSE_WAYLAND_WSI:BOOL=ON \
 -DUSE_SYSTEM_LIBSDL2:BOOL=ON \
 -DLIBRETRO:BOOL=OFF \
%if %{with qt}
 -DUSING_QT_UI:BOOL=ON \
%endif
 %{common_build_options}
%make_build -C build

%install
%make_install -C build

# Install PPSSPP executable
mkdir -p %{buildroot}%{_bindir}
%if %{with qt}
install -pm 755 build/PPSSPPQt %{buildroot}%{_bindir}/
desktop-file-install -m 644 %SOURCE5 --dir=%{buildroot}%{_datadir}/applications
desktop-file-install -m 644 %SOURCE7 --dir=%{buildroot}%{_datadir}/applications
%endif
%if %{without qt}
install -pm 755 build/PPSSPPSDL %{buildroot}%{_bindir}/
%endif

# Install libraries
mkdir -p %{buildroot}%{_libdir}/%{name}
%if %{with qt}
cp -a build/lib/lib*.* %{buildroot}%{_libdir}/%{name}/
# Install data files
mkdir -p %{buildroot}%{_datadir}/%{name}
cp -a build/assets %{buildroot}%{_datadir}/%{name}/
install -pm 644 Qt/languages/*.ts %{buildroot}%{_datadir}/%{name}/assets/lang/
%endif
cp -u build/lib/lib*.* %{buildroot}%{_libdir}/%{name}/

%if %{with ffmpeg}
pushd ffmpeg/linux/%{__arch}/lib
install -pm 755 *.so* %{buildroot}%{_libdir}/%{name}/
popd
pushd %{buildroot}%{_libdir}/%{name}
ln -sf libavcodec.so.57.24.102 libavcodec.so.57
ln -sf libavcodec.so.57.24.102 libavcodec.so
ln -sf libavformat.so.57.25.100 libavformat.so.57
ln -sf libavformat.so.57.25.100 libavformat.so
ln -sf libavutil.so.55.17.103 libavutil.so.55
ln -sf libavutil.so.55.17.103 libavutil.so
ln -sf libswresample.so.2.0.101 libswresample.so.2
ln -sf libswresample.so.2.0.101 libswresample.so
ln -sf libswscale.so.4.0.100 libswscale.so.4
ln -sf libswscale.so.4.0.100 libswscale.so
popd
%endif

# Fix rpaths
patchelf --set-rpath %{_libdir}/%{name} %{buildroot}%{_bindir}/PPSSPP*
patchelf --set-rpath %{_libdir}/%{name} %{buildroot}%{_libdir}/%{name}/*.so*

# Remove unnecessary files
rm -rf %{buildroot}%{_includedir}

# Install icons
mkdir -p %{buildroot}%{_datadir}/icons/%{name}
cp -a icons/hicolor %{buildroot}%{_datadir}/icons/
install -pm 644 icons/icon-114.png %{buildroot}%{_datadir}/icons/%{name}/%{name}.png

# Install desktop file
mkdir -p %{buildroot}%{_datadir}/applications
%if %{without qt}
desktop-file-install -m 644 %SOURCE3 --dir=%{buildroot}%{_datadir}/applications
%endif


# Already installed
rm -f %{buildroot}%{_datadir}/applications/PPSSPPSDL.desktop
rm -f %{buildroot}%{_datadir}/applications/PPSSPPQt.desktop

# Install appdata file
mkdir -p %{buildroot}%{_metainfodir}
%if %{with qt}
install -pm 644 %SOURCE6 %{buildroot}%{_metainfodir}/
%else
install -pm 644 %SOURCE4 %{buildroot}%{_metainfodir}/
%endif
appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/*.appdata.xml

%if %{without qt}
%files sdl
%doc README.md
%license LICENSE.TXT
%{_bindir}/PPSSPPSDL
%{_datadir}/applications/%{name}.desktop
%{_metainfodir}/%{name}.appdata.xml
%endif

%if %{with qt}
%files qt
%doc README.md
%license LICENSE.TXT
%{_bindir}/PPSSPPQt
%{_datadir}/applications/%{name}-qt.desktop
%{_datadir}/applications/%{name}-qt-wayland.desktop
%{_metainfodir}/%{name}-qt.appdata.xml
%endif

%files libs
%doc README.md
%license LICENSE.TXT
%if %{with ffmpeg}
%license ffmpeg/COPYING* ffmpeg/LICENSE.md
%endif
%{_libdir}/%{name}/

%files data
%doc README.md
%license LICENSE.TXT
%{_datadir}/icons/hicolor/scalable/apps/ppsspp.svg
%{_datadir}/mime/packages/ppsspp.xml
%{_datadir}/%{name}/
%{_datadir}/icons/hicolor/*/apps/%{name}.png
%{_datadir}/icons/%{name}/

%changelog
* Tue Jun 17 2025 Antonio Trande <sagitter@fedoraproject.org> - 1.19.2-1
- Release 1.19.2
- Explicitely disable BUILD_SHARED_LIBS CMake option
- Use SYSTEM_MINIUPNPC

* Sun Apr 06 2025 Antonio Trande <sagitter@fedoraproject.org> - 1.18.1-3
- Active USE_WAYLAND_WSI CMake option

* Fri Jan 31 2025 Antonio Trande <sagitter@fedoraproject.org> - 1.18.1-2
- Fix libraries link

* Thu Jan 30 2025 Antonio Trande <sagitter@fedoraproject.org> - 1.18.1-1
- Release 1.18.1

* Tue Jan 28 2025 RPM Fusion Release Engineering <sergiomb@rpmfusion.org> - 1.18-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_42_Mass_Rebuild

* Sun Nov 03 2024 Antonio Trande <sagitter@fedoraproject.org> - 1.18-1
- Release 1.18

* Fri Aug 02 2024 RPM Fusion Release Engineering <sergiomb@rpmfusion.org> - 1.17.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_41_Mass_Rebuild

* Tue Feb 06 2024 Antonio Trande <sagitter@fedoraproject.org> - 1.17.1-1
- Release 1.17.1

* Sun Feb 04 2024 RPM Fusion Release Engineering <sergiomb@rpmfusion.org> - 1.16.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_40_Mass_Rebuild

* Sun Oct 15 2023 Antonio Trande <sagitter@fedoraproject.org> - 1.16.6-1
- Release 1.16.6

* Tue Oct 03 2023 Antonio Trande <sagitter@fedoraproject.org> - 1.16.5-1
- Release 1.16.5

* Wed Sep 27 2023 Antonio Trande <sagitter@fedoraproject.org> - 1.16.4-1
- Release 1.16.4

* Sun Sep 24 2023 Antonio Trande <sagitter@fedoraproject.org> - 1.16.3-1
- Release 1.16.3

* Wed Aug 02 2023 RPM Fusion Release Engineering <sergiomb@rpmfusion.org> - 1.15.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_39_Mass_Rebuild

* Sat May 27 2023 Antonio Trande <sagitter@fedoraproject.org> - 1.15.4-1
- Release 1.15.4

* Sun May 07 2023 Antonio Trande <sagitter@fedoraproject.org> - 1.15.3-1
- Release 1.15.3

* Thu May 04 2023 Antonio Trande <sagitter@fedoraproject.org> - 1.15.2-1
- Release 1.15.2

* Sun Apr 30 2023 Antonio Trande <sagitter@fedoraproject.org> - 1.15-1
- Release 1.15

* Fri Jan 06 2023 Antonio Trande <sagitter@fedoraproject.org> - 1.14.4-1
- Release 1.14.4

* Sat Dec 31 2022 Antonio Trande <sagitter@fedoraproject.org> - 1.14.2-1
- Release 1.14.2

* Thu Dec 15 2022 Antonio Trande <sagitter@fedoraproject.org> - 1.14-1
- Release 1.14

* Sat Sep 24 2022 Antonio Trande <sagitter@fedoraproject.org> - 1.13.2-1
- Release 1.13.2

* Sat Aug 20 2022 Antonio Trande <sagitter@fedoraproject.org> - 1.13.1-2
- Fix QT_QPA_PLATFORM env variables

* Tue Aug 09 2022 Antonio Trande <sagitter@fedoraproject.org> - 1.13.1-1
- Release 1.13.1 including bundled FFMpeg-3.0.2

* Sun Aug 07 2022 RPM Fusion Release Engineering <sergiomb@rpmfusion.org> - 1.13-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_37_Mass_Rebuild and ffmpeg
  5.1

* Thu Jul 28 2022 Antonio Trande <sagitter@fedoraproject.org> - 1.13-1
- Release 1.13 including bundled FFMpeg-3.0.2

* Sun Feb 06 2022 Antonio Trande <sagitter@fedoraproject.org> - 1.12.3-2
- Source archive re-generated including bundled FFMpeg
- Rebuild against bundled FFMpeg-3.0.2 (upstream bug #15308)

* Wed Oct 20 2021 Antonio Trande <sagitter@fedoraproject.org> - 1.12.3-1
- Release 1.12.3

* Wed Oct 13 2021 Antonio Trande <sagitter@fedoraproject.org> - 1.12.2-1
- Release 1.12.2

* Sat Oct 09 2021 Antonio Trande <sagitter@fedoraproject.org> - 1.12.1-1
- Release 1.12.1

* Fri Oct 08 2021 Antonio Trande <sagitter@fedoraproject.org> - 1.12-1
- Release 1.12
- Enable USING_EGL/USING_GLES2 options

* Tue Aug 03 2021 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 1.11.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_35_Mass_Rebuild

* Sat Apr 24 2021 Antonio Trande <sagitter@fedoraproject.org> - 1.11.3-1
- Release 1.11.3

* Sat Apr 24 2021 Leigh Scott <leigh123linux@gmail.com> - 1.11-4
- Rebuilt for removed libstdc++ symbol (#1937698)

* Sat Feb 20 2021 Antonio Trande <sagitter@fedoraproject.org> - 1.11-3
- Unbundle FFmpeg (upstream bug #13849)

* Mon Feb 08 2021 Antonio Trande <sagitter@fedoraproject.org> - 1.11-2
- Change filtering method of private libraries

* Mon Feb 08 2021 Antonio Trande <sagitter@fedoraproject.org> - 1.11-1
- Release 1.11

* Wed Feb 03 2021 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 1.10.3-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Sun Jan 10 2021 Antonio Trande <sagitter@fedoraproject.org> - 1.10.3-7
- Use bundled FFMpeg-3.0.2 in Fedora 34 (RPM Fusion bz#5889)

* Fri Jan  1 2021 Leigh Scott <leigh123linux@gmail.com> - 1.10.3-6
- Rebuilt for new ffmpeg snapshot

* Sun Dec 13 2020 Antonio Trande <sagitter@fedoraproject.org> - 1.10.3-5
- Fix CMake options
- Add make BR

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

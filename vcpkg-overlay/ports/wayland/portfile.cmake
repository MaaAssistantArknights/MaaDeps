#[[
修改内容

1. 更改 wayland 的版本
2. 改为使用 GitHub 镜像源
3. 为移动 wayland-scanner 和 aclocal 的逻辑添加判断条件 NOT VCPKG_CROSSCOMPILING
4. 手动编译了 scanner 并直接在 meson 中引用, 而非查找

]]

vcpkg_check_features(OUT_FEATURE_OPTIONS FEATURE_OPTIONS
    FEATURES
        "force-build" FORCE_BUILD
)

if(NOT X_VCPKG_FORCE_VCPKG_WAYLAND_LIBRARIES AND NOT VCPKG_TARGET_IS_WINDOWS AND NOT FORCE_BUILD)
    message(STATUS "Utils and libraries provided by '${PORT}' should be provided by your system! Install the required packages or force vcpkg libraries by setting X_VCPKG_FORCE_VCPKG_WAYLAND_LIBRARIES")
    set(VCPKG_POLICY_EMPTY_PACKAGE enabled)
else()


if (NOT FORCE_BUILD OR NOT X_VCPKG_FORCE_VCPKG_WAYLAND_LIBRARIES)
    message(FATAL_ERROR "To build wayland libraries the `force-build` feature must be enabled and the X_VCPKG_FORCE_VCPKG_WAYLAND_LIBRARIES triplet variable must be set.")
endif()

vcpkg_from_github(
    OUT_SOURCE_PATH SOURCE_PATH
    REPO gitlab-freedesktop-mirrors/wayland
    # ubuntu 22.04 1.20.0
    # REF 75c1a93e2067220fa06208f20f8f096bb463ec08
    # SHA512 c0c07843db0c6bfe0475f757cc9147692338cf5e5bb7a94549399b700a5c4e72d264d2caa325a2b6590c032fd7a9e3456dfe2f2530e1988887ee69a0a62cab52
    # ubuntu 24.04 1.22.0
    REF b2649cb3ee6bd70828a17e50beb16591e6066288
    SHA512 6f2dce620bff1cd2ddd858ab1f7022d1133d9aa37c14431bdb2ab6296696c59ea6c28f40c59a8f8a92332ad03d1679a2b5854c0aaa914e9ca8db53438fddc4ea
    PATCHES
        001-fix-scanner-path.patch
)

if(VCPKG_CROSSCOMPILING)
    set(OPTIONS -Dscanner=false -Dscanner_path=${CMAKE_CURRENT_LIST_DIR}/wayland-scanner)
else()
    set(OPTIONS -Dscanner=true)
endif()

vcpkg_configure_meson(
    SOURCE_PATH "${SOURCE_PATH}"
    OPTIONS -Ddtd_validation=false
            -Ddocumentation=false
            -Dtests=false
            ${OPTIONS}
)
vcpkg_install_meson()

if(EXISTS "${CURRENT_PACKAGES_DIR}/lib/" AND VCPKG_LIBRARY_LINKAGE STREQUAL static)
    file(INSTALL "${CURRENT_BUILDTREES_DIR}/${TARGET_TRIPLET}-rel/src/${VCPKG_TARGET_STATIC_LIBRARY_PREFIX}wayland-private${VCPKG_TARGET_STATIC_LIBRARY_SUFFIX}"
                 DESTINATION "${CURRENT_PACKAGES_DIR}/lib")
    file(INSTALL "${CURRENT_BUILDTREES_DIR}/${TARGET_TRIPLET}-rel/src/${VCPKG_TARGET_STATIC_LIBRARY_PREFIX}wayland-util${VCPKG_TARGET_STATIC_LIBRARY_SUFFIX}"
             DESTINATION "${CURRENT_PACKAGES_DIR}/lib")
endif()
if(EXISTS "${CURRENT_PACKAGES_DIR}/debug/lib/" AND VCPKG_LIBRARY_LINKAGE STREQUAL static)
    file(INSTALL "${CURRENT_BUILDTREES_DIR}/${TARGET_TRIPLET}-dbg/src/${VCPKG_TARGET_STATIC_LIBRARY_PREFIX}wayland-private${VCPKG_TARGET_STATIC_LIBRARY_SUFFIX}"
                 DESTINATION "${CURRENT_PACKAGES_DIR}/debug/lib")
    file(INSTALL "${CURRENT_BUILDTREES_DIR}/${TARGET_TRIPLET}-dbg/src/${VCPKG_TARGET_STATIC_LIBRARY_PREFIX}wayland-util${VCPKG_TARGET_STATIC_LIBRARY_SUFFIX}"
                 DESTINATION "${CURRENT_PACKAGES_DIR}/debug/lib")
endif()
vcpkg_fixup_pkgconfig()

file(REMOVE_RECURSE "${CURRENT_PACKAGES_DIR}/debug/include")
file(REMOVE_RECURSE "${CURRENT_PACKAGES_DIR}/debug/share")

# Handle copyright
file(INSTALL "${SOURCE_PATH}/COPYING" DESTINATION "${CURRENT_PACKAGES_DIR}/share/${PORT}" RENAME copyright)

if(NOT VCPKG_CROSSCOMPILING)
    file(MAKE_DIRECTORY "${CURRENT_PACKAGES_DIR}/tools/${PORT}")
    file(RENAME "${CURRENT_PACKAGES_DIR}/bin/wayland-scanner${VCPKG_TARGET_EXECUTABLE_SUFFIX}" "${CURRENT_PACKAGES_DIR}/tools/${PORT}/wayland-scanner${VCPKG_TARGET_EXECUTABLE_SUFFIX}")
    file(MAKE_DIRECTORY  "${CURRENT_PACKAGES_DIR}/share/${PORT}")
    file(RENAME "${CURRENT_PACKAGES_DIR}/share/aclocal" "${CURRENT_PACKAGES_DIR}/share/${PORT}/aclocal")
endif()
if(VCPKG_LIBRARY_LINKAGE STREQUAL static OR NOT VCPKG_TARGET_IS_WINDOWS)
        file(REMOVE_RECURSE "${CURRENT_PACKAGES_DIR}/bin" "${CURRENT_PACKAGES_DIR}/debug/bin")
endif()

set(_file "${CURRENT_PACKAGES_DIR}/lib/pkgconfig/wayland-scanner.pc")
if(EXISTS "${_file}")
    file(READ "${_file}" _contents)
    string(REPLACE "bindir=\${prefix}/bin" "bindir=\${prefix}/tools/${PORT}" _contents "${_contents}")
    file(WRITE "${_file}" "${_contents}")
endif()

set(_file "${CURRENT_PACKAGES_DIR}/debug/lib/pkgconfig/wayland-scanner.pc")
if(EXISTS "${_file}")
    file(READ "${_file}" _contents)
    string(REPLACE "bindir=\${prefix}/bin" "bindir=\${prefix}/../tools/${PORT}" _contents "${_contents}")
    file(WRITE "${_file}" "${_contents}")
endif()
endif()

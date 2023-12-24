set(VCPKG_TARGET_ARCHITECTURE arm64)
set(VCPKG_CRT_LINKAGE dynamic)
set(VCPKG_CMAKE_SYSTEM_NAME Android)
set(VCPKG_CMAKE_SYSTEM_VERSION 23)
set(VCPKG_BUILD_TYPE release)
set(VCPKG_MAKE_BUILD_TRIPLET "--host=aarch64-linux-android")
set(VCPKG_CMAKE_CONFIGURE_OPTIONS ${VCPKG_CMAKE_CONFIGURE_OPTIONS}
    -DANDROID_ABI=arm64-v8a
    -DCMAKE_SHARED_LINKER_FLAGS="-Wl,-s")

include(${CMAKE_CURRENT_LIST_DIR}/maa-linux-library-override.cmake)
include(${CMAKE_CURRENT_LIST_DIR}/maa-android-library-override.cmake)

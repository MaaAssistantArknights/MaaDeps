set(VCPKG_TARGET_ARCHITECTURE arm64)
set(VCPKG_CRT_LINKAGE dynamic)
set(VCPKG_CMAKE_SYSTEM_NAME Android)
set(VCPKG_CMAKE_SYSTEM_VERSION 23)
set(VCPKG_BUILD_TYPE release)
set(VCPKG_MAKE_BUILD_TRIPLET "--host=aarch64-linux-android")
set(VCPKG_CMAKE_CONFIGURE_OPTIONS ${VCPKG_CMAKE_CONFIGURE_OPTIONS} -DANDROID_USE_LEGACY_TOOLCHAIN_FILE=OFF
                                    -DCMAKE_SHARED_LINKER_FLAGS="-Wl,-s")

include(${CMAKE_CURRENT_LIST_DIR}/maa-linux-library-override.cmake.inc)

if(PORT MATCHES "onnxruntime")
    message("add -Wno-error=shorten-64-to-32 for ${PORT}")
    add_compile_options(" -Wno-error=shorten-64-to-32")
endif()

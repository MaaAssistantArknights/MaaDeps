set(VCPKG_TARGET_ARCHITECTURE x64)
set(VCPKG_CRT_LINKAGE dynamic)
set(VCPKG_BUILD_TYPE release)
set(VCPKG_CMAKE_SYSTEM_NAME Linux)
set(VCPKG_MAKE_BUILD_TRIPLET "--host=x86_64-linux-gnu")

set(VCPKG_CHAINLOAD_TOOLCHAIN_FILE "${CMAKE_CURRENT_LIST_DIR}/../../cmake/maa-x64-linux-toolchain.cmake")

include(${CMAKE_CURRENT_LIST_DIR}/maa-linux-library-override.cmake)

# incompatible onnx version

if (VCPKG_LIBRARY_LINKAGE STREQUAL "static")
    set(VCPKG_POLICY_DLLS_IN_STATIC_LIBRARY enabled) # onnxruntime_providers_shared is always built and is a dynamic library
endif()

vcpkg_from_github(
    OUT_SOURCE_PATH SOURCE_PATH
    REPO microsoft/onnxruntime
    REF v1.18.0
    SHA512 2e1d724eda5635fc24f93966412c197c82ee933aaea4f4ce907b5f2ee7730c1e741f2ef4d50a2d54284fc7bd05bf104bd3c56fd4466525fcd70e63c07fbb2b16
    PATCHES
        0000-system-lib-fix.patch
        0001-coreml-proto.patch
)

vcpkg_find_acquire_program(PYTHON3)
set(FLATC_EXECUTABLE "${CURRENT_HOST_INSTALLED_DIR}/tools/flatbuffers/flatc${VCPKG_TARGET_EXECUTABLE_SUFFIX}")
vcpkg_execute_build_process(
    COMMAND "${PYTHON3}" compile_schema.py --flatc "${FLATC_EXECUTABLE}"
    WORKING_DIRECTORY "${SOURCE_PATH}/onnxruntime/core/flatbuffers/schema"
    LOGNAME LOGNAME "flatbuffers-compile-${TARGET_TRIPLET}"
)

set(PLATFORM_OPTIONS )

if(VCPKG_TARGET_IS_WINDOWS)
    set(PLATFORM_OPTIONS ${PLATFORM_OPTIONS} "-Donnxruntime_USE_DML=ON")
elseif(VCPKG_TARGET_IS_OSX)
    set(PLATFORM_OPTIONS ${PLATFORM_OPTIONS} "-Donnxruntime_USE_COREML=ON")
endif()

vcpkg_cmake_configure(
    SOURCE_PATH "${SOURCE_PATH}/cmake"
    OPTIONS
    "-DFETCHCONTENT_FULLY_DISCONNECTED=ON"
    "-Donnxruntime_BUILD_SHARED_LIB=ON"
    "-Donnxruntime_BUILD_UNIT_TESTS=OFF"
    "-DProtobuf_USE_STATIC_LIBS=ON"
    "-Donnxruntime_USE_PREINSTALLED_EIGEN=ON"
    "-DFLATBUFFERS_BUILD_FLATC=OFF"
    "-DCMAKE_INSTALL_INCLUDEDIR=include"
    ${PLATFORM_OPTIONS}
    OPTIONS_RELEASE
    "-Donnxruntime_ENABLE_LTO=ON"
)
vcpkg_cmake_install()
vcpkg_cmake_config_fixup(CONFIG_PATH lib/cmake/onnxruntime)
vcpkg_fixup_pkgconfig()
vcpkg_copy_pdbs()

file(INSTALL "${SOURCE_PATH}/LICENSE" DESTINATION "${CURRENT_PACKAGES_DIR}/share/${PORT}" RENAME copyright)
file(REMOVE_RECURSE "${CURRENT_PACKAGES_DIR}/debug/include")

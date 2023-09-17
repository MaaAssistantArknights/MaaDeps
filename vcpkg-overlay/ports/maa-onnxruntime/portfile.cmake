# incompatible onnx version

if (VCPKG_LIBRARY_LINKAGE STREQUAL "static")
    set(VCPKG_POLICY_DLLS_IN_STATIC_LIBRARY enabled) # onnxruntime_providers_shared is always built and is a dynamic library
endif()

vcpkg_from_github(
    OUT_SOURCE_PATH SOURCE_PATH
    REPO microsoft/onnxruntime
    REF v1.15.1
    SHA512 c9ad2ab1102bb97bdd88aa8e06432fff2960fb21172891eee9631ff7cbbdf3366cd7cf5c0baa494eb883135eab47273ed3128851ff4d9adfa004a479e941b6b5
    PATCHES
        0000-system-lib-fix.patch
        0001-suppress-depracation-warnings.patch
        0002-pkgconfig-prefix.patch
)

vcpkg_find_acquire_program(PYTHON3)
set(FLATC_EXECUTABLE "${CURRENT_HOST_INSTALLED_DIR}/tools/flatbuffers/flatc${VCPKG_TARGET_EXECUTABLE_SUFFIX}")
vcpkg_execute_build_process(
    COMMAND "${PYTHON3}" compile_schema.py --flatc "${FLATC_EXECUTABLE}"
    WORKING_DIRECTORY "${SOURCE_PATH}/onnxruntime/core/flatbuffers/schema"
    LOGNAME LOGNAME "flatbuffers-compile-${TARGET_TRIPLET}"
)

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
    OPTIONS_RELEASE
    "-Donnxruntime_ENABLE_LTO=ON"
)
vcpkg_cmake_install()
vcpkg_copy_pdbs()

file(INSTALL "${SOURCE_PATH}/LICENSE" DESTINATION "${CURRENT_PACKAGES_DIR}/share/${PORT}" RENAME copyright)
file(REMOVE_RECURSE "${CURRENT_PACKAGES_DIR}/debug/include")

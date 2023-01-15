# incompatible onnx version

if (VCPKG_LIBRARY_LINKAGE STREQUAL "static")
    set(VCPKG_POLICY_DLLS_IN_STATIC_LIBRARY enabled) # onnxruntime_providers_shared is always built and is a dynamic library
endif()

vcpkg_from_github(
    OUT_SOURCE_PATH SOURCE_PATH
    REPO microsoft/onnxruntime
    REF v1.12.1
    SHA512 fc2e8be54fbeb32744c8882e61aa514be621eb621a073d05a85c6e2deac8c9bf1103e746711f5c33a4fa55a257807ba0159d9f23684f4926ff38b40591575d91
    PATCHES
        0000-system-lib-fix.patch
)
# vcpkg_find_acquire_program(GIT)

# set(SOURCE_PATH "${CURRENT_BUILDTREES_DIR}/src/maa-onnxruntime-1.12.1")

# make_directory("${SOURCE_PATH}")

# set(onnxruntime_GIT_REF 70481649e3c2dba0f0e1728d15a00e440084a217)  # v1.12.1

# # download
# if(NOT EXISTS "${SOURCE_PATH}/.git")
#     vcpkg_execute_required_process(
#         ALLOW_IN_DOWNLOAD_MODE
#         COMMAND "${GIT}" init -b unused_branch
#         WORKING_DIRECTORY "${SOURCE_PATH}"
#         LOGNAME LOGNAME "maa-onnxruntime-fetch-${TARGET_TRIPLET}"
#     )
# endif()
# vcpkg_execute_required_process(
#     ALLOW_IN_DOWNLOAD_MODE
#     COMMAND "${GIT}" fetch --depth 1 https://github.com/microsoft/onnxruntime "${onnxruntime_GIT_REF}"
#     WORKING_DIRECTORY "${SOURCE_PATH}"
#     LOGNAME LOGNAME "maa-onnxruntime-fetch-${TARGET_TRIPLET}"
# )
# vcpkg_execute_required_process(
#     ALLOW_IN_DOWNLOAD_MODE
#     COMMAND "${GIT}" reset --hard FETCH_HEAD
#     WORKING_DIRECTORY "${SOURCE_PATH}"
#     LOGNAME LOGNAME "maa-onnxruntime-fetch-${TARGET_TRIPLET}"
# )
# vcpkg_apply_patches(
#     SOURCE_PATH "${SOURCE_PATH}"
#     PATCHES 0000-system-lib-fix.patch
# )

# foreach(submodule onnx)
#     vcpkg_execute_required_process(
#         ALLOW_IN_DOWNLOAD_MODE
#         COMMAND "${GIT}" submodule update --init --recommend-shallow --depth 1 "cmake/external/${submodule}" 
#         WORKING_DIRECTORY "${SOURCE_PATH}"
#         LOGNAME LOGNAME "maa-onnxruntime-fetch-${TARGET_TRIPLET}"
#     )
# endforeach()

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
    "-Donnxruntime_BUILD_SHARED_LIB=ON"
    "-Donnxruntime_BUILD_UNIT_TESTS=OFF"
    "-Donnxruntime_ENABLE_LTO=ON"
    "-DCMAKE_INTERPROCEDURAL_OPTIMIZATION=ON"
    "-Donnxruntime_PREFER_SYSTEM_LIB=ON"
    "-DProtobuf_USE_STATIC_LIBS=ON"
    "-Donnxruntime_USE_PREINSTALLED_EIGEN=ON"
    "-DFLATBUFFERS_BUILD_FLATC=OFF"
    "-DCMAKE_INSTALL_INCLUDEDIR=include"
)
vcpkg_cmake_install()
vcpkg_copy_pdbs()

file(INSTALL "${SOURCE_PATH}/LICENSE" DESTINATION "${CURRENT_PACKAGES_DIR}/share/${PORT}" RENAME copyright)

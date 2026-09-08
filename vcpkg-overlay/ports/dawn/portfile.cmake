# NOTE: dynamic library vs. static library
#
# We are building Dawn as a shared library `webgpu_dawn`. However, we need to set the `BUILD_SHARED_LIBS` option to
# `OFF` in this portfile. See the explanation below.
#
# In CMake convention, the `BUILD_SHARED_LIBS` option is used to control whether a library is built as a shared library or a static library.
# However, in the Dawn repository, there are multiple targets. Instead of building each target as a shared library, Dawn
# uses a CMake option `DAWN_BUILD_MONOLITHIC_LIBRARY` to control whether to build a monolithic dynamic library.
#
# When `DAWN_BUILD_MONOLITHIC_LIBRARY` is set to `ON`, a single library is built that contains all the targets. The
# library is always built as a shared library, regardless of the value of `BUILD_SHARED_LIBS`.
#
# In the vcpkg migration, we found that when both `DAWN_BUILD_MONOLITHIC_LIBRARY` and `BUILD_SHARED_LIBS` are set to `ON`, the build process will fail with some unexpected errors.
# So we need to set `BUILD_SHARED_LIBS` to `OFF` in this mode.
#
# The following function call ensures BUILD_SHARED_LIBS is set to OFF.
vcpkg_check_linkage(ONLY_STATIC_LIBRARY)

if(VCPKG_TARGET_IS_EMSCRIPTEN)
    message(FATAL_ERROR "This port is currently not supported on Emscripten.")
endif()

set(onnxruntime_vcpkg_DAWN_OPTIONS)

list(APPEND onnxruntime_vcpkg_DAWN_OPTIONS

    # enable the vcpkg flag
    -DDAWN_ENABLE_VCPKG=ON

    # fetch dependencies is disabled when using vcpkg
    -DDAWN_FETCH_DEPENDENCIES=OFF

    -DDAWN_BUILD_SAMPLES=OFF
    -DDAWN_ENABLE_NULL=OFF
    -DDAWN_BUILD_TESTS=OFF
)

if (NOT VCPKG_TARGET_IS_EMSCRIPTEN)
    list(APPEND onnxruntime_vcpkg_DAWN_OPTIONS

        -DDAWN_BUILD_MONOLITHIC_LIBRARY=SHARED
        -DDAWN_ENABLE_INSTALL=ON

        -DDAWN_ENABLE_DESKTOP_GL=OFF
        -DDAWN_ENABLE_OPENGLES=OFF
        -DDAWN_SUPPORTS_GLFW_FOR_WINDOWING=OFF
        -DDAWN_USE_GLFW=OFF
        -DDAWN_USE_WINDOWS_UI=OFF
        -DTINT_BUILD_GLSL_WRITER=OFF
        -DTINT_BUILD_GLSL_VALIDATOR=OFF

        -DDAWN_DXC_ENABLE_ASSERTS_IN_NDEBUG=OFF
        -DDAWN_USE_X11=OFF

        -DTINT_BUILD_TESTS=OFF
        -DTINT_BUILD_CMD_TOOLS=OFF
        -DTINT_BUILD_IR_BINARY=OFF
        -DTINT_BUILD_SPV_READER=OFF
        -DTINT_BUILD_WGSL_WRITER=ON

        -DDAWN_BUILD_PROTOBUF=OFF

        -DDAWN_ENABLE_SPIRV_VALIDATION=OFF


    )
endif()

if(VCPKG_TARGET_IS_WINDOWS)
    # feature detection on Windows
    vcpkg_check_features(OUT_FEATURE_OPTIONS FEATURE_OPTIONS
        FEATURES
        windows-use-d3d12 onnxruntime_vcpkg_ENABLE_DAWN_BACKEND_D3D12
        windows-use-vulkan onnxruntime_vcpkg_ENABLE_DAWN_BACKEND_VULKAN
    )

    list(APPEND onnxruntime_vcpkg_DAWN_OPTIONS
        -DDAWN_USE_BUILT_DXC=ON
        -DTINT_BUILD_HLSL_WRITER=ON
    )

    if((NOT onnxruntime_vcpkg_ENABLE_DAWN_BACKEND_VULKAN) AND(NOT onnxruntime_vcpkg_ENABLE_DAWN_BACKEND_D3D12))
        message(FATAL_ERROR "At least one of \"windows-use-d3d12\" or \"windows-use-vulkan\" must be enabled when using Dawn on Windows.")
    endif()

    if(onnxruntime_vcpkg_ENABLE_DAWN_BACKEND_VULKAN)
        list(APPEND onnxruntime_vcpkg_DAWN_OPTIONS
            -DDAWN_ENABLE_VULKAN=ON
            -DTINT_BUILD_SPV_WRITER=ON
        )
    else()
        list(APPEND onnxruntime_vcpkg_DAWN_OPTIONS
            -DDAWN_ENABLE_VULKAN=OFF
        )
    endif()

    if(onnxruntime_vcpkg_ENABLE_DAWN_BACKEND_D3D12)
        list(APPEND onnxruntime_vcpkg_DAWN_OPTIONS
            -DDAWN_ENABLE_D3D12=ON
        )
    else()
        list(APPEND onnxruntime_vcpkg_DAWN_OPTIONS
            -DDAWN_ENABLE_D3D12=OFF
        )
    endif()

    # We are currently always using the D3D12 backend.
    list(APPEND onnxruntime_vcpkg_DAWN_OPTIONS
        -DDAWN_ENABLE_D3D11=OFF
    )
endif()

vcpkg_from_github(
    OUT_SOURCE_PATH SOURCE_PATH
    REPO google/dawn
    REF "${VERSION}"
    SHA512 787d0e311acd6c5242fd9675e3766b9326098860ea80536f8bf2d8aaa9f2ea4312cef9c7b9c76529b46986e8009631ac2f30355458757c55de5bfa64d1e25960

    PATCHES
      # dawn.patch
      # dawn_force_enable_f16_nvidia_vulkan.patch
      dawn_vcpkg_integration.patch
)

function(z_vcpkg_from_git_to_path)
    cmake_parse_arguments(PARSE_ARGV 0 arg "" "OUT_SOURCE_PATH;URL;REF" "PATCHES")
    if(EXISTS "${arg_OUT_SOURCE_PATH}")
        file(GLOB children LIST_DIRECTORIES true "${arg_OUT_SOURCE_PATH}/*")
        if(NOT "${children}" STREQUAL "")
            message(FATAL_ERROR "The path ${arg_OUT_SOURCE_PATH} already exists and is not empty.")
        else()
            file(REMOVE_RECURSE "${arg_OUT_SOURCE_PATH}")
        endif()
        unset(children)
    endif()
    vcpkg_from_git(
        OUT_SOURCE_PATH out_source_path
        URL "${arg_URL}"
        REF "${arg_REF}"
        PATCHES ${arg_PATCHES}
    )
    file(RENAME "${out_source_path}" "${arg_OUT_SOURCE_PATH}")
    file(REMOVE_RECURSE "${out_source_path}")
endfunction()

z_vcpkg_from_git_to_path(
    OUT_SOURCE_PATH "${SOURCE_PATH}/third_party/jinja2"
    URL "https://chromium.googlesource.com/chromium/src/third_party/jinja2"
    REF c3027d884967773057bf74b957e3fea87e5df4d7
)

z_vcpkg_from_git_to_path(
    OUT_SOURCE_PATH "${SOURCE_PATH}/third_party/markupsafe"
    URL "https://chromium.googlesource.com/chromium/src/third_party/markupsafe"
    REF 4256084ae14175d38a3ff7d739dca83ae49ccec6
)

vcpkg_find_acquire_program(PYTHON3)

vcpkg_cmake_configure(
    SOURCE_PATH "${SOURCE_PATH}"
    WINDOWS_USE_MSBUILD
    OPTIONS
    ${onnxruntime_vcpkg_DAWN_OPTIONS}
    "-DPython3_EXECUTABLE=${PYTHON3}"

    # MAYBE_UNUSED_VARIABLES
)

vcpkg_cmake_install()
file(MAKE_DIRECTORY "${CURRENT_PACKAGES_DIR}/share/dawn/cmake")
file(RENAME "${CURRENT_PACKAGES_DIR}/lib/cmake/Dawn" "${CURRENT_PACKAGES_DIR}/share/dawn/cmake")

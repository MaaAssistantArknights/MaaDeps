set(VCPKG_LIBRARY_LINKAGE static)

if(PORT MATCHES "^opencv")
  set(VCPKG_LIBRARY_LINKAGE dynamic)
  list(APPEND VCPKG_CMAKE_CONFIGURE_OPTIONS
    -DBUILD_opencv_ml=OFF
    -DBUILD_opencv_stitching=OFF
    -DBUILD_opencv_java_bindings_generator=OFF
    -DBUILD_opencv_js_bindings_generator=OFF
    -DBUILD_opencv_objc_bindings_generator=OFF
    -DBUILD_opencv_python_bindings_generator=OFF
    -DBUILD_opencv_python_tests=OFF
    -DBUILD_opencv_hdf=OFF
    -DBUILD_opencv_quality=OFF
  )
endif()

if(PORT STREQUAL "maa-onnxruntime")
  set(VCPKG_LIBRARY_LINKAGE dynamic)
endif()

if(PORT STREQUAL "maa-fastdeploy")
  set(VCPKG_LIBRARY_LINKAGE dynamic)
endif()

set(VCPKG_CMAKE_CONFIGURE_OPTIONS
  ${VCPKG_CMAKE_CONFIGURE_OPTIONS}
  -DCMAKE_SHARED_LIBRARY_SUFFIX_CXX=_maa.dll
  "-DCMAKE_MSVC_DEBUG_INFORMATION_FORMAT=$<$<CONFIG:Debug,RelWithDebInfo>:Embedded>"
)

find_program(CCACHE_EXE ccache)
if(NOT CCACHE_EXE AND DEFINED ENV{CMAKE_C_COMPILER_LAUNCHER})
  set(CCACHE_EXE "$ENV{CMAKE_C_COMPILER_LAUNCHER}")
endif()

if(CCACHE_EXE AND NOT "${VCPKG_CMAKE_CONFIGURE_OPTIONS}" MATCHES "CMAKE_C_COMPILER_LAUNCHER")
  list(APPEND VCPKG_CMAKE_CONFIGURE_OPTIONS
    "-DCMAKE_C_COMPILER_LAUNCHER=${CCACHE_EXE}"
    "-DCMAKE_CXX_COMPILER_LAUNCHER=${CCACHE_EXE}"
  )
endif()



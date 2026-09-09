set(VCPKG_LIBRARY_LINKAGE static)
# set(VCPKG_CMAKE_CONFIGURE_OPTIONS ${VCPKG_CMAKE_CONFIGURE_OPTIONS} -DCMAKE_SHARED_LIBRARY_SUFFIX_CXX=_maa.so)

if(PORT MATCHES "^opencv")
  set(VCPKG_LIBRARY_LINKAGE dynamic)
  list(APPEND VCPKG_CMAKE_CONFIGURE_OPTIONS
    -DWITH_V4L=OFF
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

if(PORT MATCHES "onnxruntime|maa-")
  message("setting dynamic linkage for ${PORT}")
  set(VCPKG_LIBRARY_LINKAGE dynamic)
endif()

if (PORT STREQUAL "wayland")
  set(X_VCPKG_FORCE_VCPKG_WAYLAND_LIBRARIES ON)
endif ()

set(VCPKG_LIBRARY_LINKAGE static)
# set(VCPKG_CMAKE_CONFIGURE_OPTIONS ${VCPKG_CMAKE_CONFIGURE_OPTIONS} -DCMAKE_SHARED_LIBRARY_SUFFIX_CXX=_maa.so)

if(PORT STREQUAL "opencv4")
  set(VCPKG_LIBRARY_LINKAGE dynamic)
  set(VCPKG_CMAKE_CONFIGURE_OPTIONS ${VCPKG_CMAKE_CONFIGURE_OPTIONS} -DWITH_V4L=OFF)
endif()

if(PORT MATCHES "onnxruntime|maa-")
  message("setting dynamic linkage for ${PORT}")
  set(VCPKG_LIBRARY_LINKAGE dynamic)
endif()

if (PORT STREQUAL "opencv")
    list(APPEND VCPKG_CMAKE_CONFIGURE_OPTIONS -DBUILD_opencv_hdf=OFF -DBUILD_opencv_quality=OFF)
endif ()

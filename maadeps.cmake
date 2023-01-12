if(NOT DEFINED MAADEPS_TRIPLET)
  find_package(Python3 COMPONENTS Interpreter REQUIRED)
  execute_process(COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_LIST_DIR}/maadeps/host_triplet.py" OUTPUT_VARIABLE VCPKG_HOST_TRIPLET OUTPUT_STRIP_TRAILING_WHITESPACE)
  set(MAADEPS_TRIPLET "maa-${VCPKG_HOST_TRIPLET}" CACHE STRING "")
  message(STATUS "MaaDeps triplet: ${MAADEPS_TRIPLET}")
endif()
if(NOT EXISTS "${CMAKE_CURRENT_LIST_DIR}/vcpkg/installed/${MAADEPS_TRIPLET}")
  message(FATAL_ERROR
    " "
    " Dependencies not found for ${MAADEPS_TRIPLET}\n"
    " run MaaDeps/download.py to download prebuilt binaries\n"
    " or MaaDeps/build.py to build from source\n"
  )
endif()
list(APPEND CMAKE_PREFIX_PATH "${CMAKE_CURRENT_LIST_DIR}/vcpkg/installed/${MAADEPS_TRIPLET}")

function(maadeps_install)
  set(basedir "${CMAKE_CURRENT_FUNCTION_LIST_DIR}/runtime/${MAADEPS_TRIPLET}")
  file(GLOB_RECURSE MAADEPS_RUNTIME_FILES "${basedir}/*")
  foreach(file ${MAADEPS_RUNTIME_FILES})
    file(RELATIVE_PATH relpath "${CMAKE_CURRENT_FUNCTION_LIST_DIR}/runtime/${MAADEPS_TRIPLET}" "${file}")
    get_filename_component(basename "${relpath}" NAME)
    get_filename_component(dirname "${relpath}" DIRECTORY)
    if(dirname STREQUAL "")
      set(dirname ".")
    endif()
    string(MAKE_C_IDENTIFIER "${basename}" identifier)
    add_library("__maadeps_runtime_${identifier}" IMPORTED SHARED)
    set_target_properties("__maadeps_runtime_${identifier}" PROPERTIES IMPORTED_LOCATION "${file}")
    message(STATUS "MaaDeps: adding ${relpath} to ${dirname}")
    install(IMPORTED_RUNTIME_ARTIFACTS "__maadeps_runtime_${identifier}" RUNTIME DESTINATION "${dirname}" LIBRARY DESTINATION "${dirname}")
  endforeach()
endfunction()


function(detect_maadeps_triplet outvar)
  string(TOLOWER "${CMAKE_SYSTEM_NAME}" maadeps_triplet_system)
  string(TOLOWER "${CMAKE_SYSTEM_PROCESSOR}" maadeps_triplet_arch)
  if(maadeps_triplet_system STREQUAL "darwin")
    set(maadeps_triplet_system "osx")
    list(LENGTH CMAKE_OSX_ARCHITECTURES osx_archcount)
    if(osx_archcount GREATER 1)
      message(FATAL_ERROR "More than one CMAKE_OSX_ARCHITECTURES is not supported")
    endif()
    set(maadeps_triplet_arch "${CMAKE_OSX_ARCHITECTURES}")
  endif()
  message("maadeps_triplet_system: ${maadeps_triplet_system}")
  message("maadeps_triplet_arch: ${maadeps_triplet_arch}")
  if(maadeps_triplet_arch MATCHES "(amd64|x86_64)")
    set(maadeps_triplet_arch "x64")
  elseif(maadeps_triplet_arch MATCHES "i[3456]86")
    set(maadeps_triplet_arch "x86")
  elseif(maadeps_triplet_arch MATCHES "(aarch64|armv8l|arm64)")
    set(maadeps_triplet_arch "arm64")
  else()
    message(FATAL_ERROR "Unrecognized CMAKE_SYSTEM_PROCESSOR: ${CMAKE_SYSTEM_PROCESSOR}")
  endif()
  set(${outvar} "maa-${maadeps_triplet_arch}-${maadeps_triplet_system}" PARENT_SCOPE)
endfunction()

if(NOT DEFINED MAADEPS_TRIPLET)
  detect_maadeps_triplet(MAADEPS_TRIPLET)
  set(MAADEPS_TRIPLET "${MAADEPS_TRIPLET}" CACHE STRING "")
  message(STATUS "Use autodetected MAADEPS_TRIPLET: ${MAADEPS_TRIPLET}, override it if not correct.")
endif()

if(NOT EXISTS "${CMAKE_CURRENT_LIST_DIR}/vcpkg/installed/${MAADEPS_TRIPLET}")
  message(FATAL_ERROR
    " "
    " Dependencies not found for ${MAADEPS_TRIPLET}\n"
    " run maadeps-download.py to download prebuilt binaries\n"
    " or maadeps-build.py to build from source\n"
  )
endif()
list(PREPEND CMAKE_FIND_ROOT_PATH "${CMAKE_CURRENT_LIST_DIR}/vcpkg/installed/${MAADEPS_TRIPLET}")

function(maadeps_install)
  install(DIRECTORY "${CMAKE_CURRENT_FUNCTION_LIST_DIR}/runtime/${MAADEPS_TRIPLET}/" DESTINATION . USE_SOURCE_PERMISSIONS)
endfunction()

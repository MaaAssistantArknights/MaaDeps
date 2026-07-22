vcpkg_check_linkage(ONLY_DYNAMIC_LIBRARY)

vcpkg_download_distfile(ARCHIVE
    URLS "https://files.pythonhosted.org/packages/source/v/vgamepad/vgamepad-${VERSION}.tar.gz"
    FILENAME "vgamepad-${VERSION}.tar.gz"
    SHA512 85c856979d77fa05b20e9fa10571f85b9be3c63fed5600e8f52cc86563513d8df11c647ae655ceab0b9940fbc7e653389713aa2aef4ba97a67bf3cfb2b6eb3d0
)

vcpkg_extract_source_archive(
    SOURCE_PATH
    ARCHIVE ${ARCHIVE}
)

if(VCPKG_TARGET_ARCHITECTURE STREQUAL "x64")
    set(VGAMEPAD_VIGEM_ARCH "x64")
elseif(VCPKG_TARGET_ARCHITECTURE STREQUAL "x86")
    set(VGAMEPAD_VIGEM_ARCH "x86")
else()
    message(FATAL_ERROR "Unsupported architecture for ${PORT}: ${VCPKG_TARGET_ARCHITECTURE}")
endif()

file(MAKE_DIRECTORY
    ${CURRENT_PACKAGES_DIR}/bin
    ${CURRENT_PACKAGES_DIR}/debug/bin
    ${CURRENT_PACKAGES_DIR}/tools
)

set(VGAMEPAD_SOURCE_ROOT "${SOURCE_PATH}")
# vcpkg_extract_source_archive() usually strips the top-level directory, but keep a fallback
# so the port remains stable if that behavior changes for .tar.gz handling.
if(NOT EXISTS "${VGAMEPAD_SOURCE_ROOT}/vgamepad/win/vigem/client/${VGAMEPAD_VIGEM_ARCH}/ViGEmClient.dll")
    if(EXISTS "${SOURCE_PATH}/vgamepad-${VERSION}/vgamepad/win/vigem/client/${VGAMEPAD_VIGEM_ARCH}/ViGEmClient.dll")
        set(VGAMEPAD_SOURCE_ROOT "${SOURCE_PATH}/vgamepad-${VERSION}")
    endif()
endif()

set(VGAMEPAD_VIGEMCLIENT_DLL
    ${VGAMEPAD_SOURCE_ROOT}/vgamepad/win/vigem/client/${VGAMEPAD_VIGEM_ARCH}/ViGEmClient.dll
)

set(VGAMEPAD_VIGEMBUS_MSI
    ${VGAMEPAD_SOURCE_ROOT}/vgamepad/win/vigem/install/${VGAMEPAD_VIGEM_ARCH}/ViGEmBusSetup_${VGAMEPAD_VIGEM_ARCH}.msi
)

if(NOT EXISTS "${VGAMEPAD_VIGEMCLIENT_DLL}")
    message(FATAL_ERROR "Expected ViGEmClient.dll not found at: ${VGAMEPAD_VIGEMCLIENT_DLL}")
endif()

if(NOT EXISTS "${VGAMEPAD_VIGEMBUS_MSI}")
    message(FATAL_ERROR "Expected ViGEmBusSetup MSI not found at: ${VGAMEPAD_VIGEMBUS_MSI}")
endif()

file(COPY "${VGAMEPAD_VIGEMCLIENT_DLL}" DESTINATION ${CURRENT_PACKAGES_DIR}/bin)
file(COPY "${VGAMEPAD_VIGEMCLIENT_DLL}" DESTINATION ${CURRENT_PACKAGES_DIR}/debug/bin)
file(COPY "${VGAMEPAD_VIGEMBUS_MSI}" DESTINATION ${CURRENT_PACKAGES_DIR}/tools)

# Handle copyright
file(INSTALL ${VGAMEPAD_SOURCE_ROOT}/LICENSE DESTINATION ${CURRENT_PACKAGES_DIR}/share/${PORT} RENAME copyright)


vcpkg_from_github(
    OUT_SOURCE_PATH SOURCE_PATH
    REPO MaaAssistantArknights/FastDeploy
    REF b7da9c53881c73a3ef993fb5f0ef232b4c56a72a
    SHA512 39bbe98b0b8a0a38b15540aeb6593e9af2716b75283f81d8a8462ddda3000920ef1b5d2a23270ba6df616b53fa4176a99583d6152c903f871fe3a16e70620832
)

vcpkg_cmake_configure(
    SOURCE_PATH "${SOURCE_PATH}"
)

vcpkg_cmake_install()

file(INSTALL "${SOURCE_PATH}/LICENSE" DESTINATION "${CURRENT_PACKAGES_DIR}/share/${PORT}" RENAME copyright)

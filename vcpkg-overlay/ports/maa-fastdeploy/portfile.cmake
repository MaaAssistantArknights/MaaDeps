vcpkg_from_github(
    OUT_SOURCE_PATH SOURCE_PATH
    REPO MaaAssistantArknights/FastDeploy
    REF 5947e66d35744cbf94a3bf20fa7e5342752d0c26
    SHA512 e69dfa5b9cd43ef0a7636970b0e14fee91a7bdaeb9483279d6b6efb9fadd09669b76960416d293b118acf1e8d649d3eb4f63aa1b8f19a25f4ddb0513d861d4ce
)

vcpkg_cmake_configure(
    SOURCE_PATH "${SOURCE_PATH}"
)

vcpkg_cmake_install()

file(INSTALL "${SOURCE_PATH}/LICENSE" DESTINATION "${CURRENT_PACKAGES_DIR}/share/${PORT}" RENAME copyright)

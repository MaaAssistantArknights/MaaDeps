vcpkg_from_github(
    OUT_SOURCE_PATH SOURCE_PATH
    REPO MaaAssistantArknights/FastDeploy
    REF 1e4f600e5e5ab23528f77b98a8c5167b46ddfce2
    SHA512 65c3bf3203fe4fd39172ee98c174b89bcf72b45e904b1ff5544da4aba45f816a4072339a165ba62e96f6055eac649e1941b0d938aa7e2ea19578d33685013c38
)

vcpkg_cmake_configure(
    SOURCE_PATH "${SOURCE_PATH}"
)

vcpkg_cmake_install()

file(INSTALL "${SOURCE_PATH}/LICENSE" DESTINATION "${CURRENT_PACKAGES_DIR}/share/${PORT}" RENAME copyright)
file(REMOVE_RECURSE "${CURRENT_PACKAGES_DIR}/debug/include")
file(REMOVE_RECURSE "${CURRENT_PACKAGES_DIR}/debug/share")

vcpkg_from_github(
    OUT_SOURCE_PATH SOURCE_PATH
    REPO MaaAssistantArknights/FastDeploy
    REF 315466ac1a4082f3c375aacab10784c25104f28f
    SHA512 702fe968898455aa0437e448eb40515fadd1f3514110753fb4eff158751d40a06557ee1fc17f05f08292c3f2dab6b4636da4507d5bc082b304b8779c0b2e37ec
)

vcpkg_cmake_configure(
    SOURCE_PATH "${SOURCE_PATH}"
)

vcpkg_cmake_install()

file(INSTALL "${SOURCE_PATH}/LICENSE" DESTINATION "${CURRENT_PACKAGES_DIR}/share/${PORT}" RENAME copyright)

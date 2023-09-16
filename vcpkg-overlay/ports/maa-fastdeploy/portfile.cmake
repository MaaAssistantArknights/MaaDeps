vcpkg_from_github(
    OUT_SOURCE_PATH SOURCE_PATH
    REPO MaaAssistantArknights/FastDeploy
    REF 5d576a9dceae33854fc9569f97251a14d7dacdbb
    SHA512 fcd255a7e130805e8346ecc977017d2f80082c46a442c20f39a9c75a2be5e3d3a50d10afe4328e6ce150b44ed1e0b6f1a8f9d0d5d21cde6c57981921709087bd
    PATCHES
        000-fix-rpath.patch
)

vcpkg_cmake_configure(
    SOURCE_PATH "${SOURCE_PATH}"
)

vcpkg_cmake_install()

file(INSTALL "${SOURCE_PATH}/LICENSE" DESTINATION "${CURRENT_PACKAGES_DIR}/share/${PORT}" RENAME copyright)
file(REMOVE_RECURSE "${CURRENT_PACKAGES_DIR}/debug/include")
file(REMOVE_RECURSE "${CURRENT_PACKAGES_DIR}/debug/share")

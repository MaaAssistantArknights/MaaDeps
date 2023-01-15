vcpkg_from_github(
    OUT_SOURCE_PATH SOURCE_PATH
    REPO MaaAssistantArknights/FastDeploy
    REF 0758d8210d3e9da1c2b44bfcf108f9777a606cc8
    SHA512 2497c2072e13344a7e1844491e018ffc3fa5c17b7ce623a73512a5fc9b907aa46cb33dff549813e0dcc6ec84a8309cca7ff4dd4db3367cf02afeb1ae0abd8e53
)

vcpkg_cmake_configure(
    SOURCE_PATH "${SOURCE_PATH}"
)

vcpkg_cmake_install()

file(INSTALL "${SOURCE_PATH}/LICENSE" DESTINATION "${CURRENT_PACKAGES_DIR}/share/${PORT}" RENAME copyright)

vcpkg_from_github(
    OUT_SOURCE_PATH SOURCE_PATH
    REPO MaaAssistantArknights/FastDeploy
    REF 7d2fdcf7949e6073b21b441787af96ea3f8c2efe
    SHA512 b3df1169eff45d17a69765c906c44fa32769c6ee665cde8c6b104caada18eddb991f504cdf6eb339a88e57900875248f91563b86681dcd03dff742a65d58ccf3
)

vcpkg_cmake_configure(
    SOURCE_PATH "${SOURCE_PATH}"
)

vcpkg_cmake_install()

file(INSTALL "${SOURCE_PATH}/LICENSE" DESTINATION "${CURRENT_PACKAGES_DIR}/share/${PORT}" RENAME copyright)

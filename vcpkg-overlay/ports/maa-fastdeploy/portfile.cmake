vcpkg_from_github(
    OUT_SOURCE_PATH SOURCE_PATH
    REPO MaaAssistantArknights/FastDeploy
    REF 0ef77d33216a7335efbe2470b1532c96c3bbf71e
    SHA512 9a328a8113707d7883e128d74217f21bd5e7241e59773709b4e8894e4491cb47b363080231399d43ced4b118e3023aaf856bef2c5a573de5091d7740ec885213
    PATCHES
        000-fix-rpath.patch
        001-fix-export.patch
)

vcpkg_cmake_configure(
    SOURCE_PATH "${SOURCE_PATH}"
)

vcpkg_cmake_install()
vcpkg_cmake_config_fixup(PACKAGE_NAME fastdeploy_ppocr CONFIG_PATH share/fastdeploy_ppocr)

file(INSTALL "${SOURCE_PATH}/LICENSE" DESTINATION "${CURRENT_PACKAGES_DIR}/share/${PORT}" RENAME copyright)
file(REMOVE_RECURSE "${CURRENT_PACKAGES_DIR}/debug/include")
file(REMOVE_RECURSE "${CURRENT_PACKAGES_DIR}/debug/share")

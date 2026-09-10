vcpkg_from_github(
    OUT_SOURCE_PATH SOURCE_PATH
    REPO SherkeyXD/FastDeploy
    REF f4494710a63244f11c841057680d32fdabfba956
    SHA512 14c667ba42ad6abea32d07ca1e4a2f0e814c4c09a42b0fa5759923c48dccbc1e9b2dc24ab5ced7bd6104145e5c882d945f2054743d4e3cac921c568ea828f7ee
)

vcpkg_cmake_configure(
    SOURCE_PATH "${SOURCE_PATH}"
)

vcpkg_cmake_install()
vcpkg_cmake_config_fixup(PACKAGE_NAME fastdeploy_ppocr CONFIG_PATH share/fastdeploy_ppocr)

file(INSTALL "${SOURCE_PATH}/LICENSE" DESTINATION "${CURRENT_PACKAGES_DIR}/share/${PORT}" RENAME copyright)
file(REMOVE_RECURSE "${CURRENT_PACKAGES_DIR}/debug/include")
file(REMOVE_RECURSE "${CURRENT_PACKAGES_DIR}/debug/share")

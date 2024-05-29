vcpkg_check_linkage(ONLY_DYNAMIC_LIBRARY)

set(VERSION 1.5.1)

vcpkg_download_distfile(ARCHIVE
    URLS "https://www.nuget.org/api/v2/package/Microsoft.AI.DirectML/1.14.1"
    FILENAME "Microsoft.AI.DirectML.1.14.1.nupkg"
    SHA512 362be04b10c5a443250909e0d57b2dc3e0e709e0651578cfea8a702e2d295b78d3d058533e728d1edd61963750c76359552dd02b1a66e8a55635347b73796637
)

vcpkg_extract_source_archive(
    SOURCE_PATH
    ARCHIVE ${ARCHIVE}
    NO_REMOVE_ONE_LEVEL
)

file(MAKE_DIRECTORY
        ${CURRENT_PACKAGES_DIR}/include
        ${CURRENT_PACKAGES_DIR}/lib
        ${CURRENT_PACKAGES_DIR}/bin
        ${CURRENT_PACKAGES_DIR}/debug/lib
        ${CURRENT_PACKAGES_DIR}/debug/bin
    )

file(COPY
        ${SOURCE_PATH}/include
        DESTINATION ${CURRENT_PACKAGES_DIR}
    )


file(COPY ${SOURCE_PATH}/bin/${VCPKG_TARGET_ARCHITECTURE}-win/DirectML.dll
    DESTINATION ${CURRENT_PACKAGES_DIR}/bin)
file(COPY ${SOURCE_PATH}/bin/${VCPKG_TARGET_ARCHITECTURE}-win/DirectML.pdb
    DESTINATION ${CURRENT_PACKAGES_DIR}/bin)
file(COPY ${SOURCE_PATH}/bin/${VCPKG_TARGET_ARCHITECTURE}-win/DirectML.lib
    DESTINATION ${CURRENT_PACKAGES_DIR}/lib)

file(COPY ${SOURCE_PATH}/bin/${VCPKG_TARGET_ARCHITECTURE}-win/DirectML.dll
    DESTINATION ${CURRENT_PACKAGES_DIR}/debug/bin)
file(COPY ${SOURCE_PATH}/bin/${VCPKG_TARGET_ARCHITECTURE}-win/DirectML.pdb
    DESTINATION ${CURRENT_PACKAGES_DIR}/debug/bin)
file(COPY ${SOURCE_PATH}/bin/${VCPKG_TARGET_ARCHITECTURE}-win/DirectML.lib
    DESTINATION ${CURRENT_PACKAGES_DIR}/debug/lib)

# file(COPY ${SOURCE_PATH}/bin/${VCPKG_TARGET_ARCHITECTURE}-win/DirectML.Debug.dll
#     DESTINATION ${CURRENT_PACKAGES_DIR}/debug/bin)
# file(COPY ${SOURCE_PATH}/bin/${VCPKG_TARGET_ARCHITECTURE}-win/DirectML.Debug.pdb
#     DESTINATION ${CURRENT_PACKAGES_DIR}/debug/bin)

# # Handle copyright
file(INSTALL ${SOURCE_PATH}/LICENSE.txt DESTINATION ${CURRENT_PACKAGES_DIR}/share/${PORT} RENAME copyright)

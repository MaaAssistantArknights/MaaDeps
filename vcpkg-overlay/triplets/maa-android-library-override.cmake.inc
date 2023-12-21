if(PORT MATCHES "onnxruntime")
    message("add -Wno-error=shorten-64-to-32 for ${PORT}")
    target_compile_options(${PORT} PRIVATE " -Wno-error=shorten-64-to-32")
endif()

# Raptor's native core
add_library(RaptorCore STATIC
    src/Raptor.cpp
)

target_include_directories(RaptorCore
    PUBLIC
        include
)

target_compile_features(RaptorCore
    PUBLIC
        cxx_std_23
)

# Raptor Python bindings
pybind11_add_module(native
    bindings/module.cpp
)

target_link_libraries(native
    PRIVATE
        RaptorCore
)

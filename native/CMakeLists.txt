# Raptor's native core
add_library(RaptorCore STATIC
    src/Raptor.cpp
)

# Force RaptorCore to build with -fPIC on Linux
if(LINUX)
    set_property(TARGET RaptorCore PROPERTY POSITION_INDEPENDENT_CODE ON)
endif()

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
    bindings/Module.cpp
)

target_link_libraries(native
    PRIVATE
        RaptorCore
)

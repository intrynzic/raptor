add_library(RaptorNative STATIC
    src/Raptor.cpp
)

target_include_directories(RaptorNative
    PUBLIC
        include
)

target_compile_features(RaptorNative
    PUBLIC
        cxx_std_23
)

cmake_minimum_required(VERSION 3.1)
project(cmake_wrapper)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

if(MINGW)
    set_source_files_properties(
            ${CMAKE_CURRENT_SOURCE_DIR}/src/arch/dotproductsse.cpp
            PROPERTIES COMPILE_FLAGS "-msse4.1")
    set_source_files_properties(
            ${CMAKE_CURRENT_SOURCE_DIR}/src/arch/intsimdmatrixsse.cpp
            PROPERTIES COMPILE_FLAGS "-msse4.1")
    set_source_files_properties(
            ${CMAKE_CURRENT_SOURCE_DIR}/src/arch/dotproductavx.cpp
            PROPERTIES COMPILE_FLAGS "-mavx")
    set_source_files_properties(
            ${CMAKE_CURRENT_SOURCE_DIR}/src/arch/intsimdmatrixavx2.cpp
            PROPERTIES COMPILE_FLAGS "-mavx2")
endif()

include("CMakeListsOriginal.txt")

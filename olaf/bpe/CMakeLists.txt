cmake_minimum_required(VERSION 3.27.2)

project(py_bpe)

add_executable(${PROJECT_NAME} binding.cpp)

find_package(pybind11 CONFIG REQUIRED)

find_package(Python COMPONENTS Development REQUIRED)
find_package(Python COMPONENTS Interpreter Development)
include_directories(${PYTHON_INCLUDE_DIRS})

#add_library(<bpe_pythlibs> ${PYTHON_INCLUDE_DIRS})
#target_link_libraries(<bpe_pythlibs> ${PYTHON_LIBRARIES})

cmake_minimum_required(VERSION 3.6)

project(pcl_display)

add_definitions(-DLINUX)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11 -g")

find_package(PCL REQUIRED)
include_directories(${PCL_INCLUDE_DIRS})
link_directories(${PCL_LIBRARY_DIRS})
add_definitions(${PCL_DEFINITIONS})

find_package(Boost REQUIRED COMPONENTS filesystem system)

include_directories(${PROJECT_SOURCE_DIR}/include)

aux_source_directory(${PROJECT_SOURCE_DIR}/src DEMO_SRCS)

add_executable(pcl_display ${DEMO_SRCS})
target_link_libraries(pcl_display pthread ${PCL_LIBRARIES} ${Boost_LIBRARIES})

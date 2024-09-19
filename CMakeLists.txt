################################################################################
#Date: September 26th, 2023                                                    #
#File: CMakeLists.txt                                                          #
#Authour: Ben Haubrich                                                         #
#Synopsis: Top level project CMakeList.txt. Note that the CMakeList.txt inside #
#          main is the CMakeLists.txt for the main `component` of the project. #
################################################################################
cmake_minimum_required(VERSION 3.5)

#Use cmake '--help-policy <POLICY>` to learn more
cmake_policy(SET CMP0079 NEW)
cmake_policy(SET CMP0076 NEW)

if (${CMAKE_HOST_SYSTEM_NAME} STREQUAL "Darwin")
  set(EXECUTABLE_SUFFIX ".Mach-O")
elseif (${CMAKE_HOST_SYSTEM_NAME} STREQUAL "Linux")
  set(EXECUTABLE_SUFFIX ".elf")
elseif (${CMAKE_HOST_SYSTEM_NAME} STREQUAL "Windows")
  set(EXECUTABLE_SUFFIX ".exe")
endif()

if (ESP_PLATFORM)
  #If not set, defaults to all components. Set this to reduce the amount of
  #components that are built at compile time. Required and linked components
  #for the ESP main component are located in the "main component" CMakeLists.txt file.
  set(COMPONENTS
    main
  )
  #Internal IDF cmake files set the target to end in .elf.
  set(EXECUTABLE_SUFFIX ".elf")
  #include directive must come after the set(COMPONENTS*) directive
  #ESP projects require the project line to be declared after the include
  include($ENV{IDF_PATH}/tools/cmake/project.cmake)
  project(mainApplication)
  include(AbstractionLayer/esp.cmake)
  target_include_directories(__idf_main PRIVATE $<TARGET_PROPERTY:abstractionLayer,INTERFACE_INCLUDE_DIRECTORIES>)
else()
  project(mainApplication)
  add_executable(${PROJECT_NAME}${EXECUTABLE_SUFFIX} "AppCode/main.cpp")

  #We can't do this for ESP projects because idf.py wants the bin directly in the build directory.
  set_target_properties(${PROJECT_NAME}${EXECUTABLE_SUFFIX}
    PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
  )

  include(AbstractionLayer/desktop.cmake)
endif()

if (${RELEASE_BUILD})
  message(STATUS "Building Release build")
  target_compile_options(${PROJECT_NAME}${EXECUTABLE_SUFFIX}
  PRIVATE
    -ffunction-sections
    -fno-exceptions
    -fdata-sections
    -Os
    -Wextra
    -std=gnu++23
  )

  target_compile_definitions(${PROJECT_NAME}${EXECUTABLE_SUFFIX} PUBLIC CONFIG_LOG_COLORS=0)

#default to debug build
else ()
  message(STATUS "Building debug build")
  target_compile_options(${PROJECT_NAME}${EXECUTABLE_SUFFIX}
  PRIVATE
    -ffunction-sections
    -fdata-sections
    -fno-exceptions
    -O0
    -g3
    -ggdb
    -Wextra
    -std=gnu++23
  )

  target_compile_definitions(${PROJECT_NAME}${EXECUTABLE_SUFFIX} PUBLIC CONFIG_LOG_COLORS=1)

endif()

add_subdirectory(AppCode)

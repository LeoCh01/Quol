cmake_minimum_required(VERSION 3.16)
project(Quol LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)

find_package(QT NAMES Qt6 Qt5 REQUIRED COMPONENTS Widgets)
find_package(Qt${QT_VERSION_MAJOR} REQUIRED COMPONENTS Widgets)

add_executable(Quol WIN32
    src/main.cpp
    src/core/AppSettingsManager.cpp
    src/core/PluginManager.cpp
    src/core/InputManager.cpp
    src/ui/ConfigWindow.cpp
    src/ui/QuolWindow.cpp
    src/ui/TitleBar.cpp
    src/ui/QuolPopupWindow.cpp
    src/ui/QuolMainWindow.cpp
    src/ui/TransitionManager.cpp
)

target_include_directories(Quol PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/src
)

target_link_libraries(Quol PRIVATE Qt${QT_VERSION_MAJOR}::Widgets)

add_library(example_plugin MODULE
    src/plugins/example/ExamplePlugin.cpp
    src/plugins/example/lib/adder.cpp
)

target_include_directories(example_plugin PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/src
)

target_link_libraries(example_plugin PRIVATE Qt${QT_VERSION_MAJOR}::Widgets)

set_target_properties(example_plugin PROPERTIES
    PREFIX ""
    OUTPUT_NAME "example"
)

add_custom_command(TARGET example_plugin POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E make_directory $<TARGET_FILE_DIR:Quol>/plugins/example/res
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        $<TARGET_FILE:example_plugin>
        $<TARGET_FILE_DIR:Quol>/plugins/example/$<TARGET_FILE_NAME:example_plugin>
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        ${CMAKE_CURRENT_SOURCE_DIR}/plugins/example/res/config.json
        $<TARGET_FILE_DIR:Quol>/plugins/example/res/config.json
)

add_library(broken_plugin MODULE
    src/plugins/broken/BrokenPlugin.cpp
)

target_include_directories(broken_plugin PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/src
)

target_link_libraries(broken_plugin PRIVATE Qt${QT_VERSION_MAJOR}::Widgets)

set_target_properties(broken_plugin PROPERTIES
    PREFIX ""
    OUTPUT_NAME "broken"
)

add_custom_command(TARGET broken_plugin POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E make_directory $<TARGET_FILE_DIR:Quol>/plugins/broken/res
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        $<TARGET_FILE:broken_plugin>
        $<TARGET_FILE_DIR:Quol>/plugins/broken/$<TARGET_FILE_NAME:broken_plugin>
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        ${CMAKE_CURRENT_SOURCE_DIR}/plugins/broken/res/config.json
        $<TARGET_FILE_DIR:Quol>/plugins/broken/res/config.json
)

add_custom_command(TARGET Quol POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        ${CMAKE_CURRENT_SOURCE_DIR}/settings.default.json
        $<TARGET_FILE_DIR:Quol>/settings.json
    COMMAND ${CMAKE_COMMAND} -E make_directory
        $<TARGET_FILE_DIR:Quol>/plugins/quol/res
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        ${CMAKE_CURRENT_SOURCE_DIR}/plugins/quol/res/config.json
        $<TARGET_FILE_DIR:Quol>/plugins/quol/res/config.json
    COMMAND ${CMAKE_COMMAND} -E make_directory
        $<TARGET_FILE_DIR:Quol>/plugins/quol/res/img
    COMMAND ${CMAKE_COMMAND} -E copy_directory
        ${CMAKE_CURRENT_SOURCE_DIR}/plugins/quol/res/img
        $<TARGET_FILE_DIR:Quol>/plugins/quol/res/img
    COMMAND ${CMAKE_COMMAND} -E make_directory
        $<TARGET_FILE_DIR:Quol>/res/styles/dark
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        ${CMAKE_CURRENT_SOURCE_DIR}/res/styles/dark/styles.qss
        $<TARGET_FILE_DIR:Quol>/res/styles/dark/styles.qss
)

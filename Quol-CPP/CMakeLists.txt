cmake_minimum_required(VERSION 3.16)
project(Quol LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOMOC_COMPILER_PREDEFINES OFF)

find_package(QT NAMES Qt6 Qt5 REQUIRED COMPONENTS Widgets Network)
find_package(Qt${QT_VERSION_MAJOR} REQUIRED COMPONENTS Widgets Network)

add_library(quol_core STATIC
    src/core/InputManager.cpp
    src/core/InputManager.hpp
    src/plugin_api/PluginConfig.cpp
    src/plugin_api/PluginConfig.hpp
)

target_include_directories(quol_core PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/src
)

target_link_libraries(quol_core PUBLIC Qt${QT_VERSION_MAJOR}::Widgets)

add_executable(Quol WIN32
    src/main.cpp
    src/core/AppSettingsManager.cpp
    src/core/PluginManager.cpp
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

target_link_libraries(Quol PRIVATE Qt${QT_VERSION_MAJOR}::Widgets quol_core)

# Build plugins
add_subdirectory(plugins/example)
add_subdirectory(plugins/chance)
add_subdirectory(plugins/colorPicker)
add_subdirectory(plugins/chat)
add_subdirectory(plugins/draw)



add_custom_command(TARGET Quol POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E make_directory
        $<TARGET_FILE_DIR:Quol>/transitions
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

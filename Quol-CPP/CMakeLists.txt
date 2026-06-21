cmake_minimum_required(VERSION 3.16)
project(Quol LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOMOC_COMPILER_PREDEFINES OFF)

# MinGW windres passes include paths unquoted to cc1, breaking paths with spaces.
# The RC file needs no autogen includes, so strip -I flags from windres entirely.
if(MINGW)
    set(CMAKE_RC_COMPILE_OBJECT
        "<CMAKE_RC_COMPILER> -O coff <DEFINES> <SOURCE> <OBJECT>")
endif()

find_package(QT NAMES Qt6 Qt5 REQUIRED COMPONENTS Widgets Network)
find_package(Qt${QT_VERSION_MAJOR} REQUIRED COMPONENTS Widgets Network)

add_library(quol_core SHARED
    src/core/InputManager.cpp
    src/core/InputManager.hpp
    src/plugin_api/PluginConfig.cpp
    src/plugin_api/PluginConfig.hpp
)

target_include_directories(quol_core PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/src
)

target_link_libraries(quol_core PUBLIC Qt${QT_VERSION_MAJOR}::Widgets)

set_target_properties(quol_core PROPERTIES
    AUTOMOC_COMPILER_PREDEFINES OFF
)

add_executable(Quol WIN32
    src/main.cpp
    src/core/AppSettingsManager.cpp
    src/core/PluginManager.cpp
    src/core/PluginStoreManager.cpp
    src/core/QuolApplication.cpp
    src/ui/ConfigWindow.cpp
    src/ui/QuolWindow.cpp
    src/ui/TitleBar.cpp
    src/ui/QuolPopupWindow.cpp
    src/ui/QuolMainWindow.cpp
    src/ui/SplashScreen.cpp
    src/ui/TransitionManager.cpp
    src/ui/UpdateNotifier.cpp
)

if (WIN32)
    file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/res
         DESTINATION ${CMAKE_CURRENT_BINARY_DIR})
    configure_file(
        ${CMAKE_CURRENT_SOURCE_DIR}/res/app_icon.rc.in
        ${CMAKE_CURRENT_BINARY_DIR}/app_icon.rc
        @ONLY
    )
    target_sources(Quol PRIVATE ${CMAKE_CURRENT_BINARY_DIR}/app_icon.rc)
endif()

target_include_directories(Quol PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/src
)

target_link_libraries(Quol PRIVATE Qt${QT_VERSION_MAJOR}::Widgets Qt${QT_VERSION_MAJOR}::Network quol_core)


add_custom_command(TARGET Quol POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E make_directory
        $<TARGET_FILE_DIR:Quol>/transitions
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        ${CMAKE_CURRENT_SOURCE_DIR}/settings.json
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
    COMMAND ${CMAKE_COMMAND} -E copy_directory
        ${CMAKE_CURRENT_SOURCE_DIR}/res
        $<TARGET_FILE_DIR:Quol>/res
)

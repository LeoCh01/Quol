add_library(keymap_plugin MODULE
    Keymap.cpp
    Keymap.hpp
    ${CMAKE_SOURCE_DIR}/src/ui/QuolPopupWindow.cpp
    ${CMAKE_SOURCE_DIR}/src/ui/TitleBar.cpp
)

target_include_directories(keymap_plugin PRIVATE
    ${CMAKE_SOURCE_DIR}/src
    ${CMAKE_SOURCE_DIR}
)

target_link_libraries(keymap_plugin PRIVATE Qt${QT_VERSION_MAJOR}::Widgets quol_core)

set_target_properties(keymap_plugin PROPERTIES
    PREFIX ""
    OUTPUT_NAME "keymap"
    AUTOMOC_COMPILER_PREDEFINES OFF
)

add_custom_command(TARGET keymap_plugin POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E make_directory $<TARGET_FILE_DIR:Quol>/plugins/keymap/res
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        $<TARGET_FILE:keymap_plugin>
        $<TARGET_FILE_DIR:Quol>/plugins/keymap/$<TARGET_FILE_NAME:keymap_plugin>
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        ${CMAKE_CURRENT_SOURCE_DIR}/res/config.json
        $<TARGET_FILE_DIR:Quol>/plugins/keymap/res/config.json
)

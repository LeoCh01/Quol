add_library(color_picker_plugin MODULE
    ColorPicker.cpp
    ColorPicker.hpp
)

target_include_directories(color_picker_plugin PRIVATE
    ${CMAKE_SOURCE_DIR}/src
    ${CMAKE_SOURCE_DIR}
)

target_link_libraries(color_picker_plugin PRIVATE Qt${QT_VERSION_MAJOR}::Widgets)

set_target_properties(color_picker_plugin PROPERTIES
    PREFIX ""
    OUTPUT_NAME "colorPicker"
    AUTOMOC_COMPILER_PREDEFINES OFF
)

add_custom_command(TARGET color_picker_plugin POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E make_directory $<TARGET_FILE_DIR:Quol>/plugins/colorPicker/res/img
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        $<TARGET_FILE:color_picker_plugin>
        $<TARGET_FILE_DIR:Quol>/plugins/colorPicker/$<TARGET_FILE_NAME:color_picker_plugin>
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        ${CMAKE_CURRENT_SOURCE_DIR}/res/config.json
        $<TARGET_FILE_DIR:Quol>/plugins/colorPicker/res/config.json
    COMMAND ${CMAKE_COMMAND} -E copy_directory
        ${CMAKE_CURRENT_SOURCE_DIR}/res/img
        $<TARGET_FILE_DIR:Quol>/plugins/colorPicker/res/img
)

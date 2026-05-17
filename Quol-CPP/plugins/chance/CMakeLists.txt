add_library(chance_plugin MODULE
    Chance.cpp
    Chance.hpp
)

target_include_directories(chance_plugin PRIVATE
    ${CMAKE_SOURCE_DIR}/src
    ${CMAKE_SOURCE_DIR}
)

target_link_libraries(chance_plugin PRIVATE Qt${QT_VERSION_MAJOR}::Widgets quol_core)

set_target_properties(chance_plugin PROPERTIES
    PREFIX ""
    OUTPUT_NAME "chance"
    AUTOMOC_COMPILER_PREDEFINES OFF
)

add_custom_command(TARGET chance_plugin POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E make_directory $<TARGET_FILE_DIR:Quol>/plugins/chance/res/img
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        $<TARGET_FILE:chance_plugin>
        $<TARGET_FILE_DIR:Quol>/plugins/chance/$<TARGET_FILE_NAME:chance_plugin>
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        ${CMAKE_CURRENT_SOURCE_DIR}/res/config.json
        $<TARGET_FILE_DIR:Quol>/plugins/chance/res/config.json
    COMMAND ${CMAKE_COMMAND} -E copy_directory
        ${CMAKE_CURRENT_SOURCE_DIR}/res/img
        $<TARGET_FILE_DIR:Quol>/plugins/chance/res/img
)

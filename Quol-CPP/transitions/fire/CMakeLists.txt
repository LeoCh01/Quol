add_library(fire MODULE
    FireTransition.cpp
)

target_include_directories(fire PRIVATE
    ${CMAKE_SOURCE_DIR}/src
)

target_link_libraries(fire PRIVATE
    Qt${QT_VERSION_MAJOR}::Widgets
)

set_target_properties(fire PROPERTIES
    PREFIX ""
    OUTPUT_NAME "fire"
    AUTOMOC_COMPILER_PREDEFINES OFF
)

add_custom_command(TARGET fire POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E make_directory $<TARGET_FILE_DIR:Quol>/transitions
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        $<TARGET_FILE:fire>
        $<TARGET_FILE_DIR:Quol>/transitions/$<TARGET_FILE_NAME:fire>
)

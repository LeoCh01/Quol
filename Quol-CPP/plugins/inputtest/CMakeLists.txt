add_library(inputtest_plugin MODULE
    InputTestPlugin.cpp
    InputTestPlugin.hpp
    ${CMAKE_SOURCE_DIR}/src/core/InputManager.cpp
)

target_include_directories(inputtest_plugin PRIVATE
    ${CMAKE_SOURCE_DIR}/src
    ${CMAKE_SOURCE_DIR}
)

target_link_libraries(inputtest_plugin PRIVATE Qt${QT_VERSION_MAJOR}::Widgets)

set_target_properties(inputtest_plugin PROPERTIES
    PREFIX ""
    OUTPUT_NAME "inputtest"
)

add_custom_command(TARGET inputtest_plugin POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E make_directory $<TARGET_FILE_DIR:Quol>/plugins/inputtest/res
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        $<TARGET_FILE:inputtest_plugin>
        $<TARGET_FILE_DIR:Quol>/plugins/inputtest/$<TARGET_FILE_NAME:inputtest_plugin>
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        ${CMAKE_CURRENT_SOURCE_DIR}/res/config.json
        $<TARGET_FILE_DIR:Quol>/plugins/inputtest/res/config.json
)

add_library(chat_plugin MODULE
    Chat.cpp
    Chat.hpp
    lib/ChatConfig.cpp
    lib/ChatConfig.hpp
    lib/SnipOverlay.cpp
    lib/SnipOverlay.hpp
    lib/providers/ProviderTypes.hpp
    lib/providers/GeminiProvider.cpp
    lib/providers/GeminiProvider.hpp
    lib/providers/GroqProvider.cpp
    lib/providers/GroqProvider.hpp
    lib/providers/OllamaProvider.cpp
    lib/providers/OllamaProvider.hpp
    ${CMAKE_SOURCE_DIR}/src/ui/QuolPopupWindow.cpp
    ${CMAKE_SOURCE_DIR}/src/ui/TitleBar.cpp
)

target_include_directories(chat_plugin PRIVATE
    ${CMAKE_SOURCE_DIR}/src
    ${CMAKE_SOURCE_DIR}
)

target_link_libraries(chat_plugin PRIVATE Qt${QT_VERSION_MAJOR}::Widgets Qt${QT_VERSION_MAJOR}::Network quol_core)

set_target_properties(chat_plugin PROPERTIES
    PREFIX ""
    OUTPUT_NAME "chat"
    AUTOMOC_COMPILER_PREDEFINES OFF
)

add_custom_command(TARGET chat_plugin POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E make_directory $<TARGET_FILE_DIR:Quol>/plugins/chat/res/img
    COMMAND ${CMAKE_COMMAND} -E make_directory $<TARGET_FILE_DIR:Quol>/plugins/chat/res/logs
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        $<TARGET_FILE:chat_plugin>
        $<TARGET_FILE_DIR:Quol>/plugins/chat/$<TARGET_FILE_NAME:chat_plugin>
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        ${CMAKE_CURRENT_SOURCE_DIR}/res/config.json
        $<TARGET_FILE_DIR:Quol>/plugins/chat/res/config.json
    COMMAND ${CMAKE_COMMAND} -E copy_directory
        ${CMAKE_CURRENT_SOURCE_DIR}/res/img
        $<TARGET_FILE_DIR:Quol>/plugins/chat/res/img
)

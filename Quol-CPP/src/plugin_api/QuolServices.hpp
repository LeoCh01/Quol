#pragma once

#include <functional>

class InputManager;

// QuolServices is passed to every plugin's initialize() call.
// It provides access to shared application services without coupling
// plugins to the full AppSettingsManager or any specific window.
class QuolServices {
public:
    explicit QuolServices(InputManager *inputManager) : m_inputManager(inputManager) {
    }

    // The single shared InputManager instance for registering hotkeys,
    // key listeners, and mouse listeners.
    InputManager *inputManager() const {
        return m_inputManager;
    }

    // Called once from main() after all plugin windows are shown.
    // Plugins can then call hide/showAllPluginWindows() e.g. for screenshots.
    void setWindowVisibilityCallbacks(std::function<void()> hide, std::function<void()> show) {
        m_hideAll = std::move(hide);
        m_showAll = std::move(show);
    }

    // Hide every Quol window (main + all plugin windows).
    void hideAllPluginWindows() const {
        if (m_hideAll)
            m_hideAll();
    }

    // Restore every Quol window after hiding.
    void showAllPluginWindows() const {
        if (m_showAll)
            m_showAll();
    }

private:
    InputManager *m_inputManager = nullptr;
    std::function<void()> m_hideAll;
    std::function<void()> m_showAll;
};

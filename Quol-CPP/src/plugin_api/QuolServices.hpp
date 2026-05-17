#pragma once

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

private:
    InputManager *m_inputManager = nullptr;
};

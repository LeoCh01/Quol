#pragma once

#include "ui/QuolWindow.hpp"

class AppSettingsManager;
class TransitionManager;
class QPushButton;

class QuolMainWindow : public QuolWindow {
    Q_OBJECT

public:
    explicit QuolMainWindow(AppSettingsManager *settings, TransitionManager *transitions, QWidget *parent = nullptr);

    void updateToggleButton();

signals:
    void mainConfigApplied(const QString &toggleKey, bool resetPos);

private:
    void copySettingsToMainConfig();
    void applyMainConfigToSettings(const QJsonObject &config);

    AppSettingsManager *m_settings;
    TransitionManager *m_transitions;
    QPushButton *m_toggleBtn = nullptr;
};

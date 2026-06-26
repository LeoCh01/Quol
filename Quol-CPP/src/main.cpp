#include <QApplication>
#include <QFile>
#include <QIcon>

#include "core/AppSettingsManager.hpp"
#include "core/LogManager.hpp"
#include "core/QuolApplication.hpp"
#include "ui/SplashScreen.hpp"
#include "ui/UpdateNotifier.hpp"

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);

    const QString baseDir = QApplication::applicationDirPath();
    LogManager logManager(baseDir);

    // App icon
    const QString iconPath = baseDir + QStringLiteral("/res/icons/icon.ico");
    if (QFile::exists(iconPath))
        app.setWindowIcon(QIcon(iconPath));

    // Settings
    AppSettingsManager settings(baseDir + QStringLiteral("/settings.json"));
    settings.load();

    // Stylesheet
    const QString style = settings.settingString(QStringLiteral("style"), QStringLiteral("dark"));
    const QString qssPath = baseDir + QStringLiteral("/res/styles/") + style + QStringLiteral("/styles.qss");
    if (QFile qss(qssPath); qss.open(QIODevice::ReadOnly | QIODevice::Text))
        app.setStyleSheet(QString::fromUtf8(qss.readAll()));

    // Block startup until update prompt is handled.
    UpdateNotifier updater(&settings);
    if (!updater.checkForUpdateBlocking())
        return 0;

    // Splash screen — shown while the app and plugins load
    SplashScreen splash(baseDir + QStringLiteral("/res/icons/splash.png"));
    splash.show();
    app.processEvents();

    // Start the application (loads plugins, registers hotkeys, shows tray)
    QuolApplication quolApp(&settings);
    quolApp.start();

    splash.close();

    return app.exec();
}

#include "ui/QuolMainWindow.hpp"
#include "core/AppSettingsManager.hpp"
#include "ui/QuolPopupWindow.hpp"
#include "ui/TransitionManager.hpp"

#include <QAbstractButton>
#include <QAbstractItemView>
#include <QApplication>
#include <QCheckBox>
#include <QCoreApplication>
#include <QDesktopServices>
#include <QDir>
#include <QFile>
#include <QFileInfo>
#include <QGridLayout>
#include <QGuiApplication>
#include <QHBoxLayout>
#include <QIcon>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QLabel>
#include <QListWidget>
#include <QMessageBox>
#include <QProcess>
#include <QPushButton>
#include <QScreen>
#include <QSet>
#include <QSignalBlocker>
#include <QSize>
#include <QStyle>
#include <QTabWidget>
#include <QUrl>
#include <QVBoxLayout>

namespace {
QJsonArray readMainDefaultGeometry() {
    const QString path = QCoreApplication::applicationDirPath() + "/plugins/quol/res/config.json";
    QFile file(path);
    if (!file.open(QIODevice::ReadOnly | QIODevice::Text)) {
        return QJsonArray{20, 20, 260, 180};
    }

    const QJsonDocument doc = QJsonDocument::fromJson(file.readAll());
    file.close();
    if (!doc.isObject()) {
        return QJsonArray{20, 20, 260, 180};
    }

    const QJsonArray cfg = doc.object().value("_").toObject().value("default_geometry").toArray();
    if (cfg.size() < 4) {
        return QJsonArray{20, 20, 260, 180};
    }

    return cfg;
}

int mainDefaultGeometryValue(int index, int fallback) {
    static const QJsonArray geometry = readMainDefaultGeometry();
    if (index < 0 || index >= geometry.size()) {
        return fallback;
    }
    return geometry.at(index).toInt(fallback);
}
}  // namespace

QuolMainWindow::QuolMainWindow(AppSettingsManager *settings, TransitionManager *transitions, QWidget *parent)
    : QuolWindow(
          "Quol",
          settings,
          mainDefaultGeometryValue(0, 20),
          mainDefaultGeometryValue(1, 20),
          mainDefaultGeometryValue(2, 260),
          mainDefaultGeometryValue(3, 180),
          parent
      )
    , m_settings(settings)
    , m_transitions(transitions) {
    copySettingsToMainConfig();
    attachConfigWindow(QCoreApplication::applicationDirPath() + "/plugins/quol/res/config.json", "Quol Config");
    setConfigSavedCallback([this](const QJsonObject &config) { applyMainConfigToSettings(config); });

    auto *grid = new QGridLayout();
    grid->setSpacing(6);

    const QString iconRoot = QCoreApplication::applicationDirPath() + "/plugins/quol/res/img/";
    const QSize iconSize(16, 16);

    auto *managePluginsBtn = new QPushButton("Manage Plugins");
    managePluginsBtn->setToolTip("Enable or disable installed plugins");
    connect(managePluginsBtn, &QPushButton::clicked, this, &QuolMainWindow::openManagePluginsDialog);
    grid->addWidget(managePluginsBtn, 0, 0, 1, 3);

    auto *versionBtn = new QPushButton();
    versionBtn->setIcon(QIcon(iconRoot + "code.svg"));
    versionBtn->setIconSize(iconSize);
    versionBtn->setToolTip("Check version on GitHub");
    connect(versionBtn, &QPushButton::clicked, this, []() {
        QDesktopServices::openUrl(QUrl("https://github.com/LeoCh01/quol"));
    });
    grid->addWidget(versionBtn, 1, 0, 1, 1);

    auto *msgBoardBtn = new QPushButton();
    msgBoardBtn->setIcon(QIcon(iconRoot + "news.svg"));
    msgBoardBtn->setIconSize(iconSize);
    msgBoardBtn->setToolTip("Message board is not implemented yet");
    grid->addWidget(msgBoardBtn, 1, 1, 1, 1);

    auto *openPluginsBtn = new QPushButton();
    openPluginsBtn->setIcon(QIcon(iconRoot + "folder.svg"));
    openPluginsBtn->setIconSize(iconSize);
    openPluginsBtn->setToolTip("Open plugins folder");
    connect(openPluginsBtn, &QPushButton::clicked, this, []() {
        const QString pluginDir = QCoreApplication::applicationDirPath() + "/plugins";
        QDesktopServices::openUrl(QUrl::fromLocalFile(QDir(pluginDir).absolutePath()));
    });
    grid->addWidget(openPluginsBtn, 1, 2, 1, 1);

    auto *reloadBtn = new QPushButton();
    reloadBtn->setIcon(QIcon(iconRoot + "reload.svg"));
    reloadBtn->setIconSize(iconSize);
    reloadBtn->setToolTip("Reload application");
    connect(reloadBtn, &QPushButton::clicked, this, &QuolMainWindow::reloadApplication);
    grid->addWidget(reloadBtn, 2, 0, 1, 1);

    auto *quitBtn = new QPushButton("Quit");
    quitBtn->setStyleSheet("background-color: #c44; color: white;");
    connect(quitBtn, &QPushButton::clicked, this, []() { QApplication::quit(); });
    grid->addWidget(quitBtn, 2, 1, 1, 2);

    addContent(grid);
}

void QuolMainWindow::updateToggleButton() {
    if (m_toggleBtn)
        m_toggleBtn->setText(m_transitions->isHidden() ? "Toggle ON" : "Toggle OFF");
}

QStringList QuolMainWindow::discoverInstalledPluginIds() const {
    const QString pluginsDirPath = QCoreApplication::applicationDirPath() + "/plugins";
    QDir pluginsDir(pluginsDirPath);

    QStringList installed;
    const QStringList folderNames = pluginsDir.entryList(QDir::Dirs | QDir::NoDotAndDotDot, QDir::Name);
    for (const QString &id : folderNames) {
        if (id.compare("quol", Qt::CaseInsensitive) == 0) {
            continue;
        }

        const QString root = pluginsDir.filePath(id);
        const QString configPath = root + "/res/config.json";
        const QString dllPath = root + "/" + id + ".dll";

        if (QFileInfo::exists(configPath) && QFileInfo::exists(dllPath)) {
            installed.append(id);
        }
    }

    return installed;
}

void QuolMainWindow::reloadApplication() const {
    QProcess::startDetached(QCoreApplication::applicationFilePath());
    QCoreApplication::quit();
}

void QuolMainWindow::openManagePluginsDialog() {
    if (!m_settings) {
        return;
    }

    if (m_pluginManagerWindow) {
        m_pluginManagerWindow->raise();
        m_pluginManagerWindow->activateWindow();
        return;
    }

    auto *popup = new QuolPopupWindow("Manage Plugins", this);
    m_pluginManagerWindow = popup;
    connect(popup, &QObject::destroyed, this, [this]() { m_pluginManagerWindow = nullptr; });
    popup->resize(420, 420);
    const QRect screen = QGuiApplication::primaryScreen()->availableGeometry();
    popup->move(screen.center().x() - 210, screen.center().y() - 210);

    auto *tabs = new QTabWidget();

    // --- Installed tab ---
    auto *installedTab = new QWidget();
    auto *installedLayout = new QVBoxLayout(installedTab);
    installedLayout->setContentsMargins(4, 4, 4, 4);
    installedLayout->setSpacing(4);

    QList<QCheckBox *> pluginChecks;
    const QStringList pluginIds = discoverInstalledPluginIds();

    auto *topRow = new QHBoxLayout();
    auto *selectAllCheck = new QCheckBox("Select All");
    topRow->addWidget(selectAllCheck);
    topRow->addStretch(1);
    auto *applyBtn = new QPushButton("Apply");
    applyBtn->setToolTip("Save and reload");
    topRow->addWidget(applyBtn);
    installedLayout->addLayout(topRow);

    QSet<QString> enabledIds;
    const QJsonArray enabledArr = m_settings->data().value("plugins").toArray();
    for (const QJsonValue &value : enabledArr) {
        enabledIds.insert(value.toString().trimmed());
    }

    if (pluginIds.isEmpty()) {
        installedLayout->addWidget(new QLabel("No installed plugins found."));
        selectAllCheck->setEnabled(false);
    } else {
        auto *listWidget = new QListWidget();
        listWidget->setSelectionMode(QAbstractItemView::NoSelection);

        for (const QString &id : pluginIds) {
            auto *itemWidget = new QWidget();
            auto *row = new QHBoxLayout(itemWidget);
            row->setContentsMargins(6, 2, 6, 2);

            const QString configPath = QCoreApplication::applicationDirPath() + "/plugins/" + id + "/res/config.json";
            QString displayName = id;
            QFile cf(configPath);
            if (cf.open(QIODevice::ReadOnly | QIODevice::Text)) {
                const QJsonDocument doc = QJsonDocument::fromJson(cf.readAll());
                cf.close();
                if (doc.isObject()) {
                    const QString title = doc.object().value("title").toString();
                    if (!title.isEmpty()) {
                        displayName = title;
                    }
                }
            }

            auto *nameLabel = new QLabel(displayName);
            auto *statusLabel = new QLabel(enabledIds.contains(id) ? "Active" : "Inactive");
            statusLabel->setObjectName(enabledIds.contains(id) ? "status-active" : "status-inactive");
            auto *check = new QCheckBox();
            check->setProperty("pluginId", id);
            check->setChecked(enabledIds.contains(id));

            connect(check, &QCheckBox::checkStateChanged, popup, [statusLabel](Qt::CheckState state) {
                const bool on = state == Qt::Checked;
                statusLabel->setText(on ? "Active" : "Inactive");
                statusLabel->setObjectName(on ? "status-active" : "status-inactive");
                statusLabel->style()->unpolish(statusLabel);
                statusLabel->style()->polish(statusLabel);
            });

            row->addWidget(nameLabel);
            row->addStretch(1);
            row->addWidget(statusLabel);
            row->addWidget(check);

            auto *item = new QListWidgetItem(listWidget);
            item->setSizeHint(QSize(0, 34));
            listWidget->addItem(item);
            listWidget->setItemWidget(item, itemWidget);

            pluginChecks.append(check);
        }

        installedLayout->addWidget(listWidget);

        bool allSelected = !pluginChecks.isEmpty();
        for (QCheckBox *check : pluginChecks) {
            if (!check->isChecked()) {
                allSelected = false;
                break;
            }
        }
        selectAllCheck->setChecked(allSelected);

        connect(selectAllCheck, &QCheckBox::checkStateChanged, popup, [pluginChecks](Qt::CheckState state) {
            const bool on = state == Qt::Checked;
            for (QCheckBox *c : pluginChecks) {
                if (c)
                    c->setChecked(on);
            }
        });

        for (QCheckBox *check : pluginChecks) {
            connect(check, &QCheckBox::checkStateChanged, popup, [pluginChecks, selectAllCheck]() {
                bool all = !pluginChecks.isEmpty();
                for (QCheckBox *c : pluginChecks) {
                    if (!c || !c->isChecked()) {
                        all = false;
                        break;
                    }
                }
                const QSignalBlocker blocker(selectAllCheck);
                selectAllCheck->setChecked(all);
            });
        }
    }

    // --- Store tab ---
    auto *storeTab = new QWidget();
    auto *storeLayout = new QVBoxLayout(storeTab);
    storeLayout->setContentsMargins(4, 4, 4, 4);
    storeLayout->addWidget(new QLabel("Plugin Store (coming soon)"));
    storeLayout->addStretch(1);

    tabs->addTab(installedTab, "Installed");
    tabs->addTab(storeTab, "Store");

    popup->addContent(tabs);

    connect(applyBtn, &QPushButton::clicked, popup, [this, popup, pluginChecks]() {
        QJsonArray selected;
        for (QCheckBox *check : pluginChecks) {
            if (check && check->isChecked()) {
                selected.append(check->property("pluginId").toString());
            }
        }

        QJsonObject &settings = m_settings->data();
        settings.insert("plugins", selected);
        if (!m_settings->save()) {
            return;
        }

        copySettingsToMainConfig();
        popup->close();
        reloadApplication();
    });

    popup->show();
    popup->raise();
    popup->activateWindow();
}

void QuolMainWindow::copySettingsToMainConfig() {
    if (!m_settings) {
        return;
    }

    const QString configPath = QCoreApplication::applicationDirPath() + "/plugins/quol/res/config.json";
    QFile file(configPath);
    QJsonObject config;

    if (file.open(QIODevice::ReadOnly | QIODevice::Text)) {
        const QJsonDocument doc = QJsonDocument::fromJson(file.readAll());
        if (doc.isObject()) {
            config = doc.object();
        }
        file.close();
    }

    config.insert("startup", m_settings->data().value("startup").toBool(false));
    config.insert("reset_pos", m_settings->data().value("is_default_pos").toBool(false));
    config.insert("toggle_key", m_settings->data().value("toggle_key").toString("`"));

    const QString transition = m_settings->data().value("transition").toString("none");
    QJsonArray transitionOptions = QJsonArray{"rand", "fade", "cursor", "up", "left", "down", "right", "none"};
    int transitionIndex = -1;
    for (int i = 0; i < transitionOptions.size(); ++i) {
        if (transitionOptions.at(i).toString() == transition) {
            transitionIndex = i;
            break;
        }
    }
    if (transitionIndex < 0) {
        transitionIndex = transitionOptions.size() - 1;
    }
    config.insert("transition", QJsonArray{transitionOptions, transitionIndex});

    QJsonObject underscore = config.value("_").toObject();
    underscore.insert("name", m_settings->data().value("name").toString("Quol"));
    underscore.insert("plugins", m_settings->data().value("plugins").toArray());
    config.insert("_", underscore);

    if (file.open(QIODevice::WriteOnly | QIODevice::Text | QIODevice::Truncate)) {
        file.write(QJsonDocument(config).toJson(QJsonDocument::Indented));
        file.close();
    }
}

void QuolMainWindow::applyMainConfigToSettings(const QJsonObject &config) {
    if (!m_settings) {
        return;
    }

    QJsonObject &settings = m_settings->data();
    settings.insert("startup", config.value("startup").toBool(settings.value("startup").toBool()));
    settings.insert("is_default_pos", config.value("reset_pos").toBool(settings.value("is_default_pos").toBool()));
    settings.insert("toggle_key", config.value("toggle_key").toString(settings.value("toggle_key").toString("`")));

    const QJsonValue transitionValue = config.value("transition");
    if (transitionValue.isArray()) {
        const QJsonArray arr = transitionValue.toArray();
        if (arr.size() == 2 && arr.at(0).isArray()) {
            const QJsonArray options = arr.at(0).toArray();
            const int idx = arr.at(1).toInt();
            if (idx >= 0 && idx < options.size()) {
                settings.insert("transition", options.at(idx).toString(settings.value("transition").toString("none")));
            }
        }
    }

    const QJsonObject underscore = config.value("_").toObject();
    if (underscore.contains("plugins") && underscore.value("plugins").isArray()) {
        settings.insert("plugins", underscore.value("plugins"));
    }

    const QString updatedToggleKey = settings.value("toggle_key").toString("`");
    const bool updatedResetPos = settings.value("is_default_pos").toBool(false);
    m_settings->save();
    emit mainConfigApplied(updatedToggleKey, updatedResetPos);
}

#include "ui/QuolMainWindow.hpp"
#include "core/AppSettingsManager.hpp"
#include "core/PluginStoreManager.hpp"
#include "ui/QuolPopupWindow.hpp"
#include "ui/TransitionManager.hpp"

#include <QAbstractButton>
#include <QAbstractItemView>
#include <QApplication>
#include <QCheckBox>
#include <QDesktopServices>
#include <QDir>
#include <QFile>
#include <QFileInfo>
#include <QGridLayout>
#include <QHBoxLayout>
#include <QIcon>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QLabel>
#include <QListWidget>
#include <QMap>
#include <QMessageBox>
#include <QProcess>
#include <QPushButton>
#include <QSet>
#include <QSettings>
#include <QSignalBlocker>
#include <QSize>
#include <QStyle>
#include <QTabWidget>
#include <QUrl>
#include <QVBoxLayout>

#include <algorithm>

namespace {
QJsonArray readMainDefaultGeometry() {
    const QString path = QApplication::applicationDirPath() + QStringLiteral("/plugins/quol/res/config.json");
    QFile file(path);
    bool opened = file.open(QIODevice::ReadOnly | QIODevice::Text);
    const QJsonDocument doc = QJsonDocument::fromJson(file.readAll());
    file.close();
    return doc.object().value(QStringLiteral("_")).toObject().value(QStringLiteral("default_geometry")).toArray();
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
          QStringLiteral("Quol"),
          settings,
          mainDefaultGeometryValue(0, 20),
          mainDefaultGeometryValue(1, 20),
          mainDefaultGeometryValue(2, 260),
          mainDefaultGeometryValue(3, 180),
          parent
      )
    , m_settings(settings)
    , m_transitions(transitions)
    , m_pluginStore(new PluginStoreManager(this)) {
    copySettingsToMainConfig();
    attachConfigWindow(
        QApplication::applicationDirPath() + QStringLiteral("/plugins/quol/res/config.json"), QStringLiteral("Quol Config")
    );
    setConfigSavedCallback([this](const QJsonObject &config) { applyMainConfigToSettings(config); });

    auto *grid = new QGridLayout();
    grid->setSpacing(6);

    const QString iconRoot = QApplication::applicationDirPath() + QStringLiteral("/plugins/quol/res/img/");
    const QSize iconSize(16, 16);

    auto *managePluginsBtn = new QPushButton(QStringLiteral("Manage Plugins"));
    managePluginsBtn->setToolTip(QStringLiteral("Enable or disable installed plugins"));
    connect(managePluginsBtn, &QPushButton::clicked, this, &QuolMainWindow::openManagePluginsDialog);
    grid->addWidget(managePluginsBtn, 0, 0, 1, 3);

    auto *versionBtn = new QPushButton();
    versionBtn->setIcon(QIcon(iconRoot + QStringLiteral("code.svg")));
    versionBtn->setIconSize(iconSize);
    versionBtn->setToolTip(QStringLiteral("Check version on GitHub"));
    connect(versionBtn, &QPushButton::clicked, this, []() {
        QDesktopServices::openUrl(QUrl(QStringLiteral("https://github.com/LeoCh01/quol")));
    });
    grid->addWidget(versionBtn, 1, 0, 1, 1);

    auto *msgBoardBtn = new QPushButton();
    msgBoardBtn->setIcon(QIcon(iconRoot + QStringLiteral("news.svg")));
    msgBoardBtn->setIconSize(iconSize);
    msgBoardBtn->setToolTip(QStringLiteral("Message board is not implemented yet"));
    grid->addWidget(msgBoardBtn, 1, 1, 1, 1);

    auto *openPluginsBtn = new QPushButton();
    openPluginsBtn->setIcon(QIcon(iconRoot + QStringLiteral("folder.svg")));
    openPluginsBtn->setIconSize(iconSize);
    openPluginsBtn->setToolTip(QStringLiteral("Open plugins folder"));
    connect(openPluginsBtn, &QPushButton::clicked, this, []() {
        const QString pluginDir = QApplication::applicationDirPath() + QStringLiteral("/plugins");
        QDesktopServices::openUrl(QUrl::fromLocalFile(QDir(pluginDir).absolutePath()));
    });
    grid->addWidget(openPluginsBtn, 1, 2, 1, 1);

    auto *reloadBtn = new QPushButton();
    reloadBtn->setIcon(QIcon(iconRoot + QStringLiteral("reload.svg")));
    reloadBtn->setIconSize(iconSize);
    reloadBtn->setToolTip(QStringLiteral("Reload application"));
    connect(reloadBtn, &QPushButton::clicked, this, &QuolMainWindow::reloadApplication);
    grid->addWidget(reloadBtn, 2, 0, 1, 1);

    auto *quitBtn = new QPushButton(QStringLiteral("Quit"));
    quitBtn->setObjectName("btn-danger");
    connect(quitBtn, &QPushButton::clicked, this, []() { QApplication::quit(); });
    grid->addWidget(quitBtn, 2, 1, 1, 2);

    addContent(grid);
}

void QuolMainWindow::updateToggleButton() {
    if (m_toggleBtn)
        m_toggleBtn->setText(m_transitions->isHidden() ? QStringLiteral("Toggle ON") : QStringLiteral("Toggle OFF"));
}

QStringList QuolMainWindow::discoverInstalledPluginIds() const {
    const QString pluginsDirPath = QApplication::applicationDirPath() + QStringLiteral("/plugins");
    QDir pluginsDir(pluginsDirPath);

    QStringList installed;
    const QStringList folderNames = pluginsDir.entryList(QDir::Dirs | QDir::NoDotAndDotDot, QDir::Name);
    for (const QString &id : folderNames) {
        if (id.compare(QStringLiteral("quol"), Qt::CaseInsensitive) == 0) {
            continue;
        }

        const QString root = pluginsDir.filePath(id);
        const QString configPath = root + QStringLiteral("/res/config.json");
        const QString dllPath = root + QStringLiteral("/") + id + QStringLiteral(".dll");

        if (QFileInfo::exists(configPath) && QFileInfo::exists(dllPath)) {
            installed.append(id);
        }
    }

    return installed;
}

QMap<QString, int> QuolMainWindow::getInstalledPluginVersions() const {
    QMap<QString, int> versions;
    const QString pluginsDir = QApplication::applicationDirPath() + QStringLiteral("/plugins");
    QDir dir(pluginsDir);
    const QStringList folderNames = dir.entryList(QDir::Dirs | QDir::NoDotAndDotDot, QDir::Name);
    for (const QString &id : folderNames) {
        if (id.compare(QStringLiteral("quol"), Qt::CaseInsensitive) == 0)
            continue;
        const QString configPath = pluginsDir + QStringLiteral("/") + id + QStringLiteral("/res/config.json");
        QFile cf(configPath);
        if (cf.open(QIODevice::ReadOnly | QIODevice::Text)) {
            const QJsonDocument doc = QJsonDocument::fromJson(cf.readAll());
            cf.close();
            const int ver =
                doc.object().value(QStringLiteral("_")).toObject().value(QStringLiteral("version")).toInt(-1);
            versions[id] = ver;
        }
    }
    return versions;
}

void QuolMainWindow::reloadApplication() const {
    QProcess::startDetached(QCoreApplication::applicationFilePath());
    QCoreApplication::quit();
}

void QuolMainWindow::openManagePluginsDialog() {
    if (m_pluginManagerWindow) {
        m_pluginManagerWindow->raise();
        m_pluginManagerWindow->activateWindow();
        return;
    }

    auto *popup = new QuolPopupWindow(QStringLiteral("Manage Plugins"), this);
    m_pluginManagerWindow = popup;
    connect(popup, &QObject::destroyed, this, [this]() { m_pluginManagerWindow = nullptr; });
    popup->resize(420, 420);

    auto *tabs = new QTabWidget();
    QList<QCheckBox *> pluginChecks;
    tabs->addTab(buildInstalledTab(popup, pluginChecks), QStringLiteral("Installed"));

    QListWidget *storeList = nullptr;
    QLabel *storeStatus = nullptr;
    tabs->addTab(buildStoreTab(popup, storeList, storeStatus), QStringLiteral("Store"));

    popup->addContent(tabs);

    connect(m_pluginStore, &PluginStoreManager::storeItemsFetchFailed, popup, [storeStatus](const QString &error) {
        storeStatus->setText(QStringLiteral("Failed to fetch store: ") + error);
    });
    connect(
        m_pluginStore,
        &PluginStoreManager::pluginDownloadFinished,
        popup,
        [this, storeStatus](const QString &pluginName, bool success) {
            if (success) {
                storeStatus->setText(QStringLiteral("\"%1\" installed. Refreshing store list...").arg(pluginName));
                m_pluginStore->fetchStoreItems();
            } else {
                storeStatus->setText(QStringLiteral("Failed to download \"%1\". Please try again.").arg(pluginName));
                m_pluginStore->fetchStoreItems();
            }
        }
    );

    popup->show();
    popup->raise();
    popup->activateWindow();
    m_pluginStore->fetchStoreItems();
}

QWidget *QuolMainWindow::buildInstalledTab(QWidget *popup, QList<QCheckBox *> &pluginChecks) {
    auto *tab = new QWidget();
    auto *layout = new QVBoxLayout(tab);
    layout->setContentsMargins(4, 4, 4, 4);
    layout->setSpacing(4);
    layout->setAlignment(Qt::AlignTop);

    const QStringList pluginIds = discoverInstalledPluginIds();

    auto *topRow = new QHBoxLayout();
    auto *selectAllCheck = new QCheckBox(QStringLiteral("Select All"));
    topRow->addWidget(selectAllCheck);
    topRow->addStretch(1);
    auto *applyBtn = new QPushButton(QStringLiteral("Apply"));
    applyBtn->setToolTip(QStringLiteral("Save and reload"));
    topRow->addWidget(applyBtn);
    layout->addLayout(topRow);

    QSet<QString> enabledIds;
    const QJsonArray enabledArr = m_settings->data().value(QStringLiteral("plugins")).toArray();
    for (const QJsonValue &value : enabledArr) {
        enabledIds.insert(value.toString().trimmed());
    }

    if (!pluginIds.isEmpty()) {
        auto *listWidget = new QListWidget();
        listWidget->setSelectionMode(QAbstractItemView::NoSelection);

        for (const QString &id : pluginIds) {
            auto *itemWidget = new QWidget();
            auto *row = new QHBoxLayout(itemWidget);
            row->setContentsMargins(6, 2, 6, 2);

            const QString configPath =
                QApplication::applicationDirPath() + QStringLiteral("/plugins/") + id + QStringLiteral("/res/config.json");
            QString displayName = id;
            QFile cf(configPath);
            if (cf.open(QIODevice::ReadOnly | QIODevice::Text)) {
                const QJsonDocument doc = QJsonDocument::fromJson(cf.readAll());
                cf.close();
                const QString title = doc.object()
                                          .value(QStringLiteral("_"))
                                          .toObject()
                                          .value(QStringLiteral("name"))
                                          .toString()
                                          .trimmed();
                displayName = title;
            }

            auto *nameLabel = new QLabel(displayName);
            auto *statusLabel =
                new QLabel(enabledIds.contains(id) ? QStringLiteral("Active") : QStringLiteral("Inactive"));
            statusLabel->setObjectName(
                enabledIds.contains(id) ? QStringLiteral("status-active") : QStringLiteral("status-inactive")
            );
            auto *check = new QCheckBox();
            check->setProperty("pluginId", id);
            check->setChecked(enabledIds.contains(id));

            connect(check, &QCheckBox::checkStateChanged, popup, [statusLabel](Qt::CheckState state) {
                const bool on = state == Qt::Checked;
                statusLabel->setText(on ? QStringLiteral("Active") : QStringLiteral("Inactive"));
                statusLabel->setObjectName(on ? QStringLiteral("status-active") : QStringLiteral("status-inactive"));
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

        layout->addWidget(listWidget);

        bool allSelected = true;
        for (QCheckBox *check : pluginChecks) {
            if (!check->isChecked()) {
                allSelected = false;
                break;
            }
        }
        selectAllCheck->setChecked(allSelected);

        connect(selectAllCheck, &QCheckBox::checkStateChanged, popup, [pluginChecks](Qt::CheckState state) {
            const bool on = state == Qt::Checked;
            for (QCheckBox *c : pluginChecks)
                c->setChecked(on);
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

    connect(applyBtn, &QPushButton::clicked, popup, [this, popup, pluginChecks]() {
        QJsonArray selected;
        for (QCheckBox *check : pluginChecks) {
            if (check->isChecked())
                selected.append(check->property("pluginId").toString());
        }
        m_settings->setValue(QStringLiteral("plugins"), selected);
        m_settings->save();
        copySettingsToMainConfig();
        popup->close();
        reloadApplication();
    });

    return tab;
}

QWidget *QuolMainWindow::buildStoreTab(QWidget *popup, QListWidget *&storeListOut, QLabel *&storeStatusOut) {
    auto *tab = new QWidget();
    auto *layout = new QVBoxLayout(tab);
    layout->setContentsMargins(4, 4, 4, 4);
    layout->setSpacing(4);

    auto *topRow = new QHBoxLayout();
    auto *storeStatusLabel = new QLabel(QStringLiteral("Loading..."));
    storeStatusLabel->setAlignment(Qt::AlignLeft | Qt::AlignVCenter);
    topRow->addWidget(storeStatusLabel, 1);
    layout->addLayout(topRow);

    auto *storeListWidget = new QListWidget();
    storeListWidget->setSelectionMode(QAbstractItemView::NoSelection);
    layout->addWidget(storeListWidget);

    storeListOut = storeListWidget;
    storeStatusOut = storeStatusLabel;

    connect(
        m_pluginStore,
        &PluginStoreManager::storeItemsFetched,
        popup,
        [this, popup, storeListWidget, storeStatusLabel](const QJsonArray &items) {
            storeListWidget->clear();
            const QMap<QString, int> installedVersions = getInstalledPluginVersions();

            struct StoreEntry {
                QString pluginName;
                int version;
                QString itemName;
            };
            QList<StoreEntry> entries;

            for (const QJsonValue &val : items) {
                const QString name = val.toObject().value(QStringLiteral("name")).toString();
                if (!name.endsWith(QStringLiteral(".zip")))
                    continue;
                const QString base = name.left(name.size() - 4);
                const int sep = base.lastIndexOf(QStringLiteral("--v"));
                if (sep != -1)
                    entries.append({base.left(sep), base.mid(sep + 3).toInt(), base});
                else
                    entries.append({base, 0, base});
            }

            std::sort(entries.begin(), entries.end(), [](const StoreEntry &a, const StoreEntry &b) {
                return a.pluginName < b.pluginName;
            });

            if (entries.isEmpty()) {
                storeStatusLabel->setText(QStringLiteral("No plugins available in the store."));
                return;
            }
            storeStatusLabel->clear();

            for (const auto &entry : entries) {
                const bool isInstalled = installedVersions.contains(entry.pluginName);
                const bool isCurrent = isInstalled && installedVersions.value(entry.pluginName) == entry.version;
                const QString displayName = entry.version > 0
                                                ? QStringLiteral("%1 (v%2)").arg(entry.pluginName).arg(entry.version)
                                                : entry.pluginName;

                auto *itemWidget = new QWidget();
                auto *row = new QHBoxLayout(itemWidget);
                row->setContentsMargins(6, 2, 6, 2);
                row->addWidget(new QLabel(displayName));
                row->addStretch(1);

                if (isCurrent) {
                    auto *lbl = new QLabel(QStringLiteral("Installed"));
                    lbl->setObjectName(QStringLiteral("status-active"));
                    lbl->setStyleSheet(QStringLiteral(
                        "padding: 4px 10px; border: 1px solid #2e7d32; border-radius: 6px; color: #2e7d32;"
                    ));
                    row->addWidget(lbl);
                } else if (isInstalled) {
                    auto *btn = new QPushButton(QStringLiteral("Update"));
                    btn->setFixedWidth(80);
                    btn->setStyleSheet(QStringLiteral(
                        "padding: 5px 10px; border: 1px solid #b58900; border-radius: 6px; color: #b58900;"
                    ));
                    const QString capturedItemName = entry.itemName;
                    connect(btn, &QPushButton::clicked, popup, [this, btn, capturedItemName]() {
                        btn->setEnabled(false);
                        btn->setText(QStringLiteral("Updating..."));
                        m_pluginStore->downloadPlugin(capturedItemName, true);
                    });
                    row->addWidget(btn);
                } else {
                    auto *btn = new QPushButton(QStringLiteral("Install"));
                    btn->setFixedWidth(80);
                    btn->setStyleSheet(QStringLiteral(
                        "padding: 5px 10px; border: 1px solid #2d6cdf; border-radius: 6px; color: #2d6cdf;"
                    ));
                    const QString capturedItemName = entry.itemName;
                    connect(btn, &QPushButton::clicked, popup, [this, btn, capturedItemName]() {
                        btn->setEnabled(false);
                        btn->setText(QStringLiteral("Installing..."));
                        m_pluginStore->downloadPlugin(capturedItemName, false);
                    });
                    row->addWidget(btn);
                }

                auto *item = new QListWidgetItem(storeListWidget);
                item->setSizeHint(QSize(0, 34));
                storeListWidget->addItem(item);
                storeListWidget->setItemWidget(item, itemWidget);
            }
        }
    );

    return tab;
}

void QuolMainWindow::copySettingsToMainConfig() {
    const QString configPath = QApplication::applicationDirPath() + QStringLiteral("/plugins/quol/res/config.json");
    QFile file(configPath);
    QJsonObject config;

    if (file.open(QIODevice::ReadOnly | QIODevice::Text)) {
        const QJsonDocument doc = QJsonDocument::fromJson(file.readAll());
        config = doc.object();
        file.close();
    }

    config.insert(QStringLiteral("startup"), m_settings->data().value(QStringLiteral("startup")).toBool(false));
    config.insert(
        QStringLiteral("reset_pos"), m_settings->data().value(QStringLiteral("is_default_pos")).toBool(false)
    );
    config.insert(
        QStringLiteral("toggle_key"),
        m_settings->data().value(QStringLiteral("toggle_key")).toString(QStringLiteral("backtick"))
    );

    QString transition =
        m_settings->data().value(QStringLiteral("transition")).toString(QStringLiteral("none")).toLower();
    QJsonArray transitionOptions = QJsonArray{
        QStringLiteral("none"),
        QStringLiteral("fade"),
        QStringLiteral("slide-left"),
        QStringLiteral("slide-right"),
        QStringLiteral("slide-up"),
        QStringLiteral("slide-down"),
        QStringLiteral("rand-slide")
    };
    int transitionIndex = -1;
    for (int i = 0; i < transitionOptions.size(); ++i) {
        if (transitionOptions.at(i).toString() == transition) {
            transitionIndex = i;
            break;
        }
    }
    if (transitionIndex < 0) {
        transitionIndex = 0;
    }
    config.insert(QStringLiteral("transition"), QJsonArray{transitionOptions, transitionIndex});

    QJsonObject underscore = config.value(QStringLiteral("_")).toObject();
    underscore.insert(
        QStringLiteral("name"), m_settings->data().value(QStringLiteral("name")).toString(QStringLiteral("Quol"))
    );
    underscore.insert(QStringLiteral("plugins"), m_settings->data().value(QStringLiteral("plugins")).toArray());
    config.insert(QStringLiteral("_"), underscore);

    if (file.open(QIODevice::WriteOnly | QIODevice::Text | QIODevice::Truncate)) {
        file.write(QJsonDocument(config).toJson(QJsonDocument::Indented));
        file.close();
    }
}

void QuolMainWindow::applyMainConfigToSettings(const QJsonObject &config) {
    const bool startup = config.value(QStringLiteral("startup")).toBool();
    m_settings->setValue(QStringLiteral("startup"), startup);

    {
        QSettings runSettings(
            QStringLiteral("HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"),
            QSettings::NativeFormat
        );
        const QString appName = m_settings->data().value(QStringLiteral("name")).toString(QStringLiteral("Quol"));
        if (startup)
            runSettings.setValue(
                appName, QStringLiteral("\"%1\"").arg(QDir::toNativeSeparators(QCoreApplication::applicationFilePath()))
            );
        else
            runSettings.remove(appName);
    }

    m_settings->setValue(QStringLiteral("is_default_pos"), config.value(QStringLiteral("reset_pos")).toBool());

    const QString toggleKey = config.value(QStringLiteral("toggle_key")).toVariant().toString().trimmed().toLower();
    m_settings->setValue(QStringLiteral("toggle_key"), toggleKey);

    const QJsonValue transitionValue = config.value(QStringLiteral("transition"));
    if (transitionValue.isArray()) {
        const QJsonArray arr = transitionValue.toArray();
        if (arr.size() == 2 && arr.at(0).isArray()) {
            const QJsonArray options = arr.at(0).toArray();
            const int idx = arr.at(1).toInt();
            if (idx >= 0 && idx < options.size()) {
                const QString selected = options.at(idx).toString().trimmed().toLower();
                m_settings->setValue(QStringLiteral("transition"), selected);
            }
        }
    }

    const QJsonObject underscore = config.value(QStringLiteral("_")).toObject();
    if (underscore.contains(QStringLiteral("plugins")) && underscore.value(QStringLiteral("plugins")).isArray()) {
        m_settings->setValue(QStringLiteral("plugins"), underscore.value(QStringLiteral("plugins")));
    }

    const QString updatedToggleKey = m_settings->data().value(QStringLiteral("toggle_key")).toString();
    const bool updatedResetPos = m_settings->data().value(QStringLiteral("is_default_pos")).toBool();
    const QString updatedTransition = m_settings->data().value(QStringLiteral("transition")).toString().toLower();
    m_settings->save();
    emit mainConfigApplied(updatedToggleKey, updatedResetPos, updatedTransition);
}

#include "ui/QuolMainWindow.hpp"
#include "ui/TransitionManager.hpp"
#include "core/AppSettingsManager.hpp"

#include <QApplication>
#include <QCoreApplication>
#include <QDesktopServices>
#include <QDir>
#include <QFile>
#include <QGridLayout>
#include <QIcon>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QPushButton>
#include <QSize>
#include <QUrl>

namespace
{
  QJsonArray readMainDefaultGeometry()
  {
    const QString path = QCoreApplication::applicationDirPath() + "/plugins/quol/res/config.json";
    QFile file(path);
    if (!file.open(QIODevice::ReadOnly | QIODevice::Text))
    {
      return QJsonArray{20, 20, 260, 180};
    }

    const QJsonDocument doc = QJsonDocument::fromJson(file.readAll());
    file.close();
    if (!doc.isObject())
    {
      return QJsonArray{20, 20, 260, 180};
    }

    const QJsonArray cfg = doc.object().value("_").toObject().value("default_geometry").toArray();
    if (cfg.size() < 4)
    {
      return QJsonArray{20, 20, 260, 180};
    }

    return cfg;
  }

  int mainDefaultGeometryValue(int index, int fallback)
  {
    static const QJsonArray geometry = readMainDefaultGeometry();
    if (index < 0 || index >= geometry.size())
    {
      return fallback;
    }
    return geometry.at(index).toInt(fallback);
  }
}

QuolMainWindow::QuolMainWindow(AppSettingsManager *settings,
                               TransitionManager *transitions,
                               QWidget *parent)
    : QuolWindow("quol", "Quol", settings,
                 mainDefaultGeometryValue(0, 20),
                 mainDefaultGeometryValue(1, 20),
                 mainDefaultGeometryValue(2, 260),
                 mainDefaultGeometryValue(3, 180),
                 parent),
      m_settings(settings), m_transitions(transitions)
{
  copySettingsToMainConfig();
  attachConfigWindow(QCoreApplication::applicationDirPath() + "/plugins/quol/res/config.json", "Quol Config");
  setConfigSavedCallback([this](const QJsonObject &config)
                         { applyMainConfigToSettings(config); });

  auto *grid = new QGridLayout();
  grid->setSpacing(6);

  const QString iconRoot = QCoreApplication::applicationDirPath() + "/plugins/quol/res/img/";
  const QSize iconSize(16, 16);

  auto *managePluginsBtn = new QPushButton("Manage Plugins");
  managePluginsBtn->setToolTip("Manage plugins UI is not implemented yet");
  grid->addWidget(managePluginsBtn, 0, 0, 1, 3);

  auto *versionBtn = new QPushButton();
  versionBtn->setIcon(QIcon(iconRoot + "code.svg"));
  versionBtn->setIconSize(iconSize);
  versionBtn->setToolTip("Check version on GitHub");
  connect(versionBtn, &QPushButton::clicked, this, []()
          { QDesktopServices::openUrl(QUrl("https://github.com/LeoCh01/quol")); });
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
  connect(openPluginsBtn, &QPushButton::clicked, this, []()
          {
        const QString pluginDir = QCoreApplication::applicationDirPath() + "/plugins";
        QDesktopServices::openUrl(QUrl::fromLocalFile(QDir(pluginDir).absolutePath())); });
  grid->addWidget(openPluginsBtn, 1, 2, 1, 1);

  auto *reloadBtn = new QPushButton();
  reloadBtn->setIcon(QIcon(iconRoot + "reload.svg"));
  reloadBtn->setIconSize(iconSize);
  reloadBtn->setToolTip("Reload application");
  connect(reloadBtn, &QPushButton::clicked, this, []()
          { QCoreApplication::quit(); });
  grid->addWidget(reloadBtn, 2, 0, 1, 1);

  auto *quitBtn = new QPushButton("Quit");
  quitBtn->setStyleSheet("background-color: #c44; color: white;");
  connect(quitBtn, &QPushButton::clicked, this, []()
          { QApplication::quit(); });
  grid->addWidget(quitBtn, 2, 1, 1, 2);

  addContent(grid);
}

void QuolMainWindow::updateToggleButton()
{
  if (m_toggleBtn)
    m_toggleBtn->setText(m_transitions->isHidden() ? "Toggle ON" : "Toggle OFF");
}

void QuolMainWindow::copySettingsToMainConfig()
{
  if (!m_settings)
  {
    return;
  }

  const QString configPath = QCoreApplication::applicationDirPath() + "/plugins/quol/res/config.json";
  QFile file(configPath);
  QJsonObject config;

  if (file.open(QIODevice::ReadOnly | QIODevice::Text))
  {
    const QJsonDocument doc = QJsonDocument::fromJson(file.readAll());
    if (doc.isObject())
    {
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
  for (int i = 0; i < transitionOptions.size(); ++i)
  {
    if (transitionOptions.at(i).toString() == transition)
    {
      transitionIndex = i;
      break;
    }
  }
  if (transitionIndex < 0)
  {
    transitionIndex = transitionOptions.size() - 1;
  }
  config.insert("transition", QJsonArray{transitionOptions, transitionIndex});

  QJsonObject underscore = config.value("_").toObject();
  underscore.insert("name", m_settings->data().value("name").toString("Quol"));
  underscore.insert("plugins", m_settings->data().value("plugins").toArray());
  config.insert("_", underscore);

  if (file.open(QIODevice::WriteOnly | QIODevice::Text | QIODevice::Truncate))
  {
    file.write(QJsonDocument(config).toJson(QJsonDocument::Indented));
    file.close();
  }
}

void QuolMainWindow::applyMainConfigToSettings(const QJsonObject &config)
{
  if (!m_settings)
  {
    return;
  }

  QJsonObject &settings = m_settings->data();
  settings.insert("startup", config.value("startup").toBool(settings.value("startup").toBool()));
  settings.insert("is_default_pos", config.value("reset_pos").toBool(settings.value("is_default_pos").toBool()));
  settings.insert("toggle_key", config.value("toggle_key").toString(settings.value("toggle_key").toString("`")));

  const QJsonValue transitionValue = config.value("transition");
  if (transitionValue.isArray())
  {
    const QJsonArray arr = transitionValue.toArray();
    if (arr.size() == 2 && arr.at(0).isArray())
    {
      const QJsonArray options = arr.at(0).toArray();
      const int idx = arr.at(1).toInt();
      if (idx >= 0 && idx < options.size())
      {
        settings.insert("transition", options.at(idx).toString(settings.value("transition").toString("none")));
      }
    }
  }

  const QJsonObject underscore = config.value("_").toObject();
  if (underscore.contains("plugins") && underscore.value("plugins").isArray())
  {
    settings.insert("plugins", underscore.value("plugins"));
  }

  m_settings->save();
}

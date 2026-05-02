#include "core/PluginManager.hpp"
#include "core/AppSettingsManager.hpp"
#include "plugin_api/IQuolPlugin.hpp"
#include "ui/QuolWindow.hpp"
#include "ui/TransitionManager.hpp"

#include <QCoreApplication>
#include <QFile>
#include <QFileInfo>
#include <QJsonArray>
#include <QJsonDocument>
#include <QLabel>
#include <QPluginLoader>

namespace
{
  QJsonArray readDefaultGeometry(const QString &configPath,
                                 int fallbackX,
                                 int fallbackY,
                                 int fallbackW,
                                 int fallbackH)
  {
    QFile file(configPath);
    if (!file.open(QIODevice::ReadOnly | QIODevice::Text))
    {
      return QJsonArray{fallbackX, fallbackY, fallbackW, fallbackH};
    }

    const QJsonDocument doc = QJsonDocument::fromJson(file.readAll());
    file.close();
    if (!doc.isObject())
    {
      return QJsonArray{fallbackX, fallbackY, fallbackW, fallbackH};
    }

    const QJsonArray cfg = doc.object().value("_").toObject().value("default_geometry").toArray();
    if (cfg.size() < 4)
    {
      return QJsonArray{fallbackX, fallbackY, fallbackW, fallbackH};
    }

    return cfg;
  }
}

PluginManager::PluginManager(QObject *parent)
    : QObject(parent)
{
}

PluginManager::~PluginManager()
{
  qDeleteAll(m_windows);
  m_windows.clear();
}

void PluginManager::loadPlugins(AppSettingsManager *settings, TransitionManager *transitions)
{
  if (!settings)
    return;

  const QString appDir = QCoreApplication::applicationDirPath();
  const QString pluginsDir = appDir + "/plugins";
  const QJsonArray pluginIds = settings->data().value("plugins").toArray();

  int y = 230;
  for (const auto &val : pluginIds)
  {
    const QString id = val.toString().trimmed();
    if (id.isEmpty())
      continue;

    QString title = id;
    if (!title.isEmpty())
      title[0] = title[0].toUpper();

    const QString libPath = pluginsDir + "/" + id + "/" + id;
    auto *loader = new QPluginLoader(libPath, this);
    auto *plugin = qobject_cast<IQuolPlugin *>(loader->instance());

    const QString configPath = pluginsDir + "/" + id + "/res/config.json";
    const QJsonArray defaultGeometry = readDefaultGeometry(configPath, 320, y, 260, 150);

    auto *win = new QuolWindow(id, plugin ? plugin->displayName() : title,
                               settings,
                               defaultGeometry.at(0).toInt(320),
                               defaultGeometry.at(1).toInt(y),
                               defaultGeometry.at(2).toInt(260),
                               defaultGeometry.at(3).toInt(150));

    if (QFileInfo::exists(configPath))
    {
      win->attachConfigWindow(configPath, title + " Config");
    }

    if (plugin)
    {
      plugin->initialize(pluginsDir + "/" + id, settings->data(), {});
      win->addContent(plugin->createWidget());
    }
    else
    {
      auto *label = new QLabel(QString("Plugin '%1' loaded.").arg(id));
      label->setWordWrap(true);
      win->addContent(label);
    }

    if (transitions)
      transitions->addWindow(win);

    m_windows.append(win);
    y += 170;
  }
}

QList<QuolWindow *> PluginManager::windows() const
{
  return m_windows;
}

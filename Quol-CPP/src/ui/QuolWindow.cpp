#include "ui/QuolWindow.hpp"
#include "ui/TitleBar.hpp"
#include "ui/ConfigWindow.hpp"
#include "core/AppSettingsManager.hpp"

#include <QCloseEvent>
#include <QFile>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QVBoxLayout>
#include <QPainterPath>
#include <QRegion>
#include <QResizeEvent>
#include <QShowEvent>

QuolWindow::QuolWindow(const QString &pluginId,
                       const QString &title,
                       AppSettingsManager *settings,
                       int defaultX,
                       int defaultY,
                       int defaultW,
                       int defaultH,
                       QWidget *parent)
    : QWidget(parent), m_pluginId(pluginId), m_titleText(title), m_settings(settings)
{
  setWindowFlags(Qt::FramelessWindowHint | Qt::WindowStaysOnTopHint | Qt::Tool);

  auto *rootLayout = new QVBoxLayout(this);
  rootLayout->setContentsMargins(0, 0, 0, 0);
  rootLayout->setSpacing(0);

  m_titleBar = new TitleBar(this, title, this);
  rootLayout->addWidget(m_titleBar);

  auto *sep = new QWidget(this);
  sep->setFixedHeight(1);
  sep->setStyleSheet("background-color: #2F2F2F;");
  rootLayout->addWidget(sep);

  auto *body = new QWidget(this);
  body->setObjectName("content");
  m_bodyLayout = new QVBoxLayout(body);
  m_bodyLayout->setContentsMargins(8, 8, 8, 8);
  m_bodyLayout->setSpacing(6);
  m_bodyLayout->setAlignment(Qt::AlignTop);
  rootLayout->addWidget(body, 1);

  loadGeometry(defaultX, defaultY, defaultW, defaultH);
  updateMask();
}

TitleBar *QuolWindow::titleBar() const
{
  return m_titleBar;
}

const QString &QuolWindow::pluginId() const
{
  return m_pluginId;
}

const QString &QuolWindow::titleText() const
{
  return m_titleText;
}

void QuolWindow::addContent(QWidget *widget)
{
  m_bodyLayout->addWidget(widget);
}

void QuolWindow::addContent(QLayout *layout)
{
  m_bodyLayout->addLayout(layout);
}

void QuolWindow::attachConfigWindow(const QString &configPath, const QString &configTitle)
{
  m_pluginConfigPath = configPath;

  if (m_configWindow)
  {
    m_configWindow->deleteLater();
    m_configWindow = nullptr;
  }

  const QString resolvedTitle = configTitle.isEmpty()
                                    ? (m_titleText + " Config")
                                    : configTitle;

  m_configWindow = new ConfigWindow(m_pluginId, resolvedTitle, m_settings, configPath, this);
  connect(m_configWindow, &ConfigWindow::configSaved, this, [this](const QJsonObject &config)
          {
        if (m_onConfigSaved)
        {
            m_onConfigSaved(config);
        }

        const QJsonObject underscore = config.value("_").toObject();
        const QJsonArray geometry = underscore.value("geometry").toArray();
        if (geometry.size() >= 4)
        {
          const int gx = geometry.at(0).toInt(x());
          const int gy = geometry.at(1).toInt(y());
          const int gw = geometry.at(2).toInt(width());
          const int gh = geometry.at(3).toInt(height());

          m_autoHeightRequested = (gh <= 0);
          setGeometry(gx,
                      gy,
                      gw,
                      (gh <= 0) ? autoHeightFromContent() : gh);
        } });

  m_titleBar->setConfigAction([this]()
                              {
      if (!m_configWindow)
      {
        return;
      }

      m_configWindow->show();
      m_configWindow->raise();
      m_configWindow->activateWindow(); });

  if (!loadGeometryFromPluginConfig())
  {
    saveGeometryToPluginConfig();
  }
}

void QuolWindow::setConfigSavedCallback(const std::function<void(const QJsonObject &)> &callback)
{
  m_onConfigSaved = callback;
}

void QuolWindow::setGeometryPersistence(bool enabled)
{
  m_persistGeometry = enabled;
}

bool QuolWindow::applyGeometryFromConfig()
{
  return loadGeometryFromPluginConfig();
}

void QuolWindow::snapToGrid()
{
  const int nx = (pos().x() / m_snapGrid) * m_snapGrid;
  const int ny = (pos().y() / m_snapGrid) * m_snapGrid;
  move(nx, ny);
  saveGeometry();
}

void QuolWindow::saveGeometry()
{
  if (!m_persistGeometry)
  {
    return;
  }

  if (saveGeometryToPluginConfig())
  {
    return;
  }

  if (m_settings)
  {
    m_settings->setWindowGeometry(m_pluginId, x(), y(), width(), height());
  }
}

void QuolWindow::resizeEvent(QResizeEvent *event)
{
  QWidget::resizeEvent(event);
  updateMask();
}

void QuolWindow::closeEvent(QCloseEvent *event)
{
  if (m_configWindow)
  {
    m_configWindow->close();
  }
  QWidget::closeEvent(event);
}

void QuolWindow::showEvent(QShowEvent *event)
{
  QWidget::showEvent(event);

  if (!m_autoHeightRequested)
  {
    return;
  }

  m_autoHeightRequested = false;
  resize(width(), autoHeightFromContent());
  saveGeometry();
}

void QuolWindow::updateMask()
{
  QPainterPath path;
  path.addRoundedRect(rect(), 6, 6);
  setMask(QRegion(path.toFillPolygon().toPolygon()));
}

void QuolWindow::loadGeometry(int defaultX, int defaultY, int defaultW, int defaultH)
{
  if (!m_persistGeometry || !m_settings)
  {
    setGeometry(defaultX, defaultY, defaultW, defaultH);
    return;
  }

  const QJsonObject configs = m_settings->data().value("configs").toObject();
  const QJsonObject pluginCfg = configs.value(m_pluginId).toObject();
  const QJsonArray geometry = pluginCfg.value("_").toObject().value("geometry").toArray();

  if (geometry.size() >= 4)
  {
    setGeometry(geometry.at(0).toInt(defaultX),
                geometry.at(1).toInt(defaultY),
                geometry.at(2).toInt(defaultW),
                geometry.at(3).toInt(defaultH));
    return;
  }

  setGeometry(defaultX, defaultY, defaultW, defaultH);
}

bool QuolWindow::loadGeometryFromPluginConfig()
{
  if (m_pluginConfigPath.isEmpty())
  {
    return false;
  }

  QFile file(m_pluginConfigPath);
  if (!file.open(QIODevice::ReadOnly | QIODevice::Text))
  {
    return false;
  }

  const QJsonDocument doc = QJsonDocument::fromJson(file.readAll());
  file.close();
  if (!doc.isObject())
  {
    return false;
  }

  QJsonObject root = doc.object();
  QJsonObject underscore = root.value("_").toObject();
  const bool hasDefaultGeometry = underscore.value("default_geometry").isArray() && underscore.value("default_geometry").toArray().size() >= 4;
  const bool useDefaultPos = m_settings && m_settings->data().value("is_default_pos").toBool(false);
  const QJsonArray defaultGeometry = underscore.value("default_geometry").toArray();
  QJsonArray geometry = underscore.value("geometry").toArray();

  bool configChanged = false;

  if (useDefaultPos && defaultGeometry.size() >= 4)
  {
    geometry = defaultGeometry;
    underscore.insert("geometry", geometry);
    root.insert("_", underscore);
    configChanged = true;
  }

  if (geometry.size() < 4)
  {
    if (defaultGeometry.size() >= 4)
    {
      geometry = defaultGeometry;
      underscore.insert("geometry", geometry);
      root.insert("_", underscore);
      configChanged = true;
    }
  }

  if (geometry.size() < 4)
  {
    return false;
  }

  const int gx = geometry.at(0).toInt(x());
  const int gy = geometry.at(1).toInt(y());
  const int gw = geometry.at(2).toInt(width());
  const int gh = geometry.at(3).toInt(height());

  m_autoHeightRequested = (gh <= 0);

  setGeometry(gx,
              gy,
              gw,
              (gh <= 0) ? autoHeightFromContent() : gh);

  if (configChanged)
  {
    if (file.open(QIODevice::WriteOnly | QIODevice::Text | QIODevice::Truncate))
    {
      file.write(QJsonDocument(root).toJson(QJsonDocument::Indented));
      file.close();
    }
  }

  if (!hasDefaultGeometry)
  {
    saveGeometryToPluginConfig();
  }

  return true;
}

bool QuolWindow::saveGeometryToPluginConfig() const
{
  if (m_pluginConfigPath.isEmpty())
  {
    return false;
  }

  QFile file(m_pluginConfigPath);
  QJsonObject root;

  if (file.exists() && file.open(QIODevice::ReadOnly | QIODevice::Text))
  {
    const QJsonDocument doc = QJsonDocument::fromJson(file.readAll());
    if (doc.isObject())
    {
      root = doc.object();
    }
    file.close();
  }

  QJsonObject underscore = root.value("_").toObject();
  if (!underscore.value("default_geometry").isArray() || underscore.value("default_geometry").toArray().size() < 4)
  {
    underscore.insert("default_geometry", QJsonArray{x(), y(), width(), 0});
  }
  underscore.insert("geometry", QJsonArray{x(), y(), width(), height()});
  root.insert("_", underscore);

  if (!file.open(QIODevice::WriteOnly | QIODevice::Text | QIODevice::Truncate))
  {
    return false;
  }

  file.write(QJsonDocument(root).toJson(QJsonDocument::Indented));
  file.close();
  return true;
}

int QuolWindow::autoHeightFromContent() const
{
  const int hint = sizeHint().height();
  const int minHint = minimumSizeHint().height();
  const int current = height();
  const int preferred = qMax(hint, minHint);
  return (preferred > 0) ? preferred : qMax(1, current);
}

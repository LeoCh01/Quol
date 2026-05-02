#pragma once

#include "plugin_api/IQuolPlugin.hpp"

#include <QObject>

class ExamplePlugin final : public QObject, public IQuolPlugin
{
  Q_OBJECT
  Q_PLUGIN_METADATA(IID IQuolPlugin_iid)
  Q_INTERFACES(IQuolPlugin)

public:
  QString pluginId() const override;
  QString displayName() const override;
  QWidget *createWidget(QWidget *parent = nullptr) override;

  QJsonObject defaultConfig() const override;
  void initialize(const QString &pluginRootPath,
                  const QJsonObject &appSettings,
                  const QJsonObject &pluginConfig) override;
  void shutdown() override;

private:
  QString m_pluginRootPath;
  QJsonObject m_appSettings;
  QJsonObject m_pluginConfig;
};

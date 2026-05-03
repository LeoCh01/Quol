#pragma once

#include "plugin_api/IQuolPlugin.hpp"

#include <QObject>

class QLabel;

class ExamplePlugin final : public QObject, public IQuolPlugin
{
  Q_OBJECT
  Q_PLUGIN_METADATA(IID IQuolPlugin_iid)
  Q_INTERFACES(IQuolPlugin)

public:
  QWidget *createWidget(QWidget *parent = nullptr) override;

  void initialize(const QString &pluginRootPath,
                  const QJsonObject &appSettings,
                  const QJsonObject &pluginConfig) override;
  void onUpdateConfig(const QJsonObject &pluginConfig) override;

private:
  void refreshLabels();

  QString m_pluginRootPath;
  QJsonObject m_appSettings;
  QJsonObject m_pluginConfig;
  QLabel *m_titleLabel = nullptr;
  QLabel *m_valueLabel = nullptr;
  QLabel *m_nestedNoteLabel = nullptr;
  QLabel *m_nestedEnabledLabel = nullptr;
  QLabel *m_nestedModeLabel = nullptr;
  QLabel *m_nestedInnerLabelLabel = nullptr;
  QLabel *m_nestedInnerChoiceLabel = nullptr;
};

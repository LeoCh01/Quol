#pragma once

#include <QWidget>
#include <functional>

class AppSettingsManager;
class TitleBar;
class QVBoxLayout;
class ConfigWindow;
class QJsonObject;

class QuolWindow : public QWidget
{
  Q_OBJECT

public:
  explicit QuolWindow(
      const QString &pluginId,
      const QString &title,
      AppSettingsManager *settings,
      int defaultX,
      int defaultY,
      int defaultW,
      int defaultH,
      QWidget *parent = nullptr);

  TitleBar *titleBar() const;
  const QString &pluginId() const;
  const QString &titleText() const;

  void addContent(QWidget *widget);
  void addContent(QLayout *layout);

  void attachConfigWindow(const QString &configPath, const QString &configTitle = QString());
  void setConfigSavedCallback(const std::function<void(const QJsonObject &)> &callback);
  void setGeometryPersistence(bool enabled);
  bool applyGeometryFromConfig();

  void snapToGrid();
  void saveGeometry();

protected:
  void resizeEvent(QResizeEvent *event) override;
  void closeEvent(QCloseEvent *event) override;
  void showEvent(QShowEvent *event) override;

private:
  void updateMask();
  void loadGeometry(int defaultX, int defaultY, int defaultW, int defaultH);
  bool loadGeometryFromPluginConfig();
  bool saveGeometryToPluginConfig() const;
  int autoHeightFromContent() const;

  QString m_pluginId;
  QString m_titleText;
  QString m_pluginConfigPath;
  AppSettingsManager *m_settings;
  TitleBar *m_titleBar = nullptr;
  QVBoxLayout *m_bodyLayout = nullptr;
  ConfigWindow *m_configWindow = nullptr;
  std::function<void(const QJsonObject &)> m_onConfigSaved;
  int m_snapGrid = 10;
  bool m_autoHeightRequested = false;
  bool m_persistGeometry = true;
};

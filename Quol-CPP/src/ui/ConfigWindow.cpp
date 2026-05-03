#include "ui/ConfigWindow.hpp"

#include "core/AppSettingsManager.hpp"

#include <QApplication>
#include <QBoxLayout>
#include <QCheckBox>
#include <QComboBox>
#include <QFile>
#include <QGroupBox>
#include <QHBoxLayout>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonValue>
#include <QLabel>
#include <QLayoutItem>
#include <QLineEdit>
#include <QPushButton>
#include <QScreen>
#include <QVBoxLayout>

namespace
{
  void clearLayoutRecursively(QLayout *layout)
  {
    if (!layout)
    {
      return;
    }

    while (QLayoutItem *item = layout->takeAt(0))
    {
      if (QWidget *widget = item->widget())
      {
        delete widget;
      }
      else if (QLayout *childLayout = item->layout())
      {
        clearLayoutRecursively(childLayout);
        delete childLayout;
      }

      delete item;
    }
  }
}

ConfigWindow::ConfigWindow(
    const QString &pluginId,
    const QString &title,
    AppSettingsManager *settings,
    const QString &configPath,
    QWidget *parent)
    : QuolWindow(pluginId + "_config", title, settings, 500, 300, 400, 240, parent), m_configPath(configPath)
{
  setGeometryPersistence(false);
  buildUi();
  reloadFromDisk();
}

void ConfigWindow::reloadFromDisk()
{
  QFile file(m_configPath);
  if (!file.exists())
  {
    m_config = QJsonObject{};
  }
  else if (file.open(QIODevice::ReadOnly | QIODevice::Text))
  {
    const auto doc = QJsonDocument::fromJson(file.readAll());
    m_config = doc.isObject() ? doc.object() : QJsonObject{};
    file.close();
  }

  clearDynamicUi();
  generateSettings();
}

void ConfigWindow::saveConfig()
{
  QJsonObject updated = extractFromLayout(m_configLayout);
  if (m_config.contains("_"))
  {
    updated.insert("_", m_config.value("_"));
  }

  QFile file(m_configPath);
  if (file.open(QIODevice::WriteOnly | QIODevice::Text | QIODevice::Truncate))
  {
    file.write(QJsonDocument(updated).toJson(QJsonDocument::Indented));
    file.close();
  }

  m_config = updated;
  emit configSaved(updated);
  hide();
}

void ConfigWindow::buildUi()
{
  m_rootContentLayout = new QVBoxLayout();
  m_rootContentLayout->setSpacing(6);

  m_configLayout = new QVBoxLayout();
  m_configLayout->setSpacing(6);
  m_rootContentLayout->addLayout(m_configLayout);

  auto *buttonLayout = new QHBoxLayout();
  auto *cancelButton = new QPushButton("Cancel");
  auto *saveButton = new QPushButton("Save");

  connect(cancelButton, &QPushButton::clicked, this, &QWidget::hide);
  connect(saveButton, &QPushButton::clicked, this, &ConfigWindow::saveConfig);

  buttonLayout->addWidget(cancelButton);
  buttonLayout->addWidget(saveButton);

  m_rootContentLayout->addLayout(buttonLayout);

  addContent(m_rootContentLayout);

  const QRect center = QApplication::primaryScreen()->availableGeometry();
  move(center.center().x() - width() / 2, center.center().y() - height() / 2);
}

void ConfigWindow::clearDynamicUi()
{
  clearLayoutRecursively(m_configLayout);
}

void ConfigWindow::generateSettings()
{
  for (auto it = m_config.begin(); it != m_config.end(); ++it)
  {
    if (it.key() == "_")
    {
      continue;
    }

    QLayout *itemLayout = createItem(it.key(), it.value());
    addItemToLayout(m_configLayout, itemLayout);
  }

  m_configLayout->invalidate();
  const int contentHeight = m_configLayout->sizeHint().height();
  const int buttonHeight = 40;
  const int verticalSpacing = 12;
  const int totalHeight = contentHeight + buttonHeight + verticalSpacing;
  resize(width(), totalHeight + 40);
}

void ConfigWindow::addItemToLayout(QLayout *layout, QLayout *itemLayout)
{
  if (auto *boxLayout = qobject_cast<QBoxLayout *>(layout))
  {
    boxLayout->addLayout(itemLayout);
    return;
  }

  layout->addItem(itemLayout);
}

void ConfigWindow::addItemToLayout(QLayout *layout, QWidget *widget)
{
  layout->addWidget(widget);
}

QLayout *ConfigWindow::createItem(const QString &key, const QJsonValue &value)
{
  if (value.isBool())
  {
    auto *row = new QHBoxLayout();
    row->addWidget(new QLabel(key));
    auto *checkbox = new QCheckBox();
    checkbox->setChecked(value.toBool());
    row->addWidget(checkbox);
    return row;
  }

  if (value.isObject())
  {
    auto *group = new QGroupBox(key);
    auto *groupLayout = new QVBoxLayout(group);

    const QJsonObject object = value.toObject();
    for (auto it = object.begin(); it != object.end(); ++it)
    {
      if (it.key() == "_")
      {
        continue;
      }

      QLayout *itemLayout = createItem(it.key(), it.value());
      addItemToLayout(groupLayout, itemLayout);
    }

    auto *wrapper = new QVBoxLayout();
    wrapper->addWidget(group);
    return wrapper;
  }

  if (value.isArray())
  {
    const QJsonArray arr = value.toArray();
    if (arr.size() == 2 && arr.at(0).isArray() && arr.at(1).isDouble())
    {
      auto *row = new QHBoxLayout();
      row->addWidget(new QLabel(key));

      auto *combo = new QComboBox();
      const QJsonArray options = arr.at(0).toArray();
      for (const auto &option : options)
      {
        combo->addItem(option.toVariant().toString());
      }

      int idx = arr.at(1).toInt();
      if (idx >= 0 && idx < combo->count())
      {
        combo->setCurrentIndex(idx);
      }

      row->addWidget(combo, 1);
      return row;
    }
  }

  auto *row = new QHBoxLayout();
  row->addWidget(new QLabel(key));
  auto *lineEdit = new QLineEdit();
  lineEdit->setText(value.toVariant().toString());
  row->addWidget(lineEdit, 1);
  return row;
}

QJsonObject ConfigWindow::extractFromLayout(QLayout *layout) const
{
  QJsonObject result;

  for (int i = 0; i < layout->count(); ++i)
  {
    QLayoutItem *item = layout->itemAt(i);
    if (!item)
    {
      continue;
    }

    QWidget *widget = item->widget();
    QLayout *subLayout = item->layout();

    if (auto *group = qobject_cast<QGroupBox *>(widget))
    {
      result.insert(group->title(), extractFromLayout(group->layout()));
      continue;
    }

    if (!subLayout)
    {
      continue;
    }

    if (subLayout->count() == 1)
    {
      QWidget *firstWidget = subLayout->itemAt(0) ? subLayout->itemAt(0)->widget() : nullptr;
      if (auto *group = qobject_cast<QGroupBox *>(firstWidget))
      {
        result.insert(group->title(), extractFromLayout(group->layout()));
        continue;
      }
    }

    if (auto *hbox = qobject_cast<QHBoxLayout *>(subLayout))
    {
      if (hbox->count() < 2)
      {
        continue;
      }

      auto *label = qobject_cast<QLabel *>(hbox->itemAt(0)->widget());
      QWidget *valueWidget = hbox->itemAt(1)->widget();
      if (!label || !valueWidget)
      {
        continue;
      }

      const QString key = label->text();

      if (auto *checkbox = qobject_cast<QCheckBox *>(valueWidget))
      {
        result.insert(key, checkbox->isChecked());
      }
      else if (auto *lineEdit = qobject_cast<QLineEdit *>(valueWidget))
      {
        result.insert(key, parseLineEditValue(lineEdit->text()));
      }
      else if (auto *combo = qobject_cast<QComboBox *>(valueWidget))
      {
        QJsonArray options;
        for (int j = 0; j < combo->count(); ++j)
        {
          options.append(combo->itemText(j));
        }
        result.insert(key, QJsonArray{options, combo->currentIndex()});
      }
    }
  }

  return result;
}

QJsonValue ConfigWindow::parseLineEditValue(const QString &text)
{
  bool intOk = false;
  const int intValue = text.toInt(&intOk);
  if (intOk)
  {
    return intValue;
  }

  bool doubleOk = false;
  const double doubleValue = text.toDouble(&doubleOk);
  if (doubleOk)
  {
    return doubleValue;
  }

  return text;
}

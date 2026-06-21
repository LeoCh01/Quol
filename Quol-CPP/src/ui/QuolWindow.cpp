#include "ui/QuolWindow.hpp"
#include "core/AppSettingsManager.hpp"
#include "ui/ConfigWindow.hpp"
#include "ui/TitleBar.hpp"

#include <QCloseEvent>
#include <QFile>
#include <QGuiApplication>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QPainterPath>
#include <QRegion>
#include <QResizeEvent>
#include <QScreen>
#include <QShowEvent>
#include <QVBoxLayout>

QuolWindow::QuolWindow(
    const QString &title,
    AppSettingsManager *settings,
    int defaultX,
    int defaultY,
    int defaultW,
    int defaultH,
    QWidget *parent
)
    : QWidget(parent), m_titleText(title), m_settings(settings) {
    setWindowFlags(Qt::FramelessWindowHint | Qt::WindowStaysOnTopHint | Qt::Tool);
    initBaseLayout(this, title, m_titleBar, m_bodyLayout);
    m_titleBar->setDragReleaseAction([this]() { snapToGrid(); });
    loadGeometry(defaultX, defaultY, defaultW, defaultH);
    updateMask();
}

void QuolWindow::initBaseLayout(
    QWidget *widget, const QString &title, TitleBar *&m_titleBarOut, QVBoxLayout *&m_bodyLayoutOut
) {
    auto *rootLayout = new QVBoxLayout(widget);
    rootLayout->setContentsMargins(0, 0, 0, 0);
    rootLayout->setSpacing(0);

    m_titleBarOut = new TitleBar(widget, title, widget);
    rootLayout->addWidget(m_titleBarOut);

    auto *sep = new QWidget(widget);
    sep->setFixedHeight(1);
    sep->setStyleSheet("background-color: #2F2F2F;");
    rootLayout->addWidget(sep);

    auto *body = new QWidget(widget);
    body->setObjectName("content");
    m_bodyLayoutOut = new QVBoxLayout(body);
    m_bodyLayoutOut->setContentsMargins(8, 8, 8, 8);
    m_bodyLayoutOut->setSpacing(6);
    m_bodyLayoutOut->setAlignment(Qt::AlignTop);
    rootLayout->addWidget(body, 1);
}

TitleBar *QuolWindow::titleBar() const {
    return m_titleBar;
}

const QString &QuolWindow::titleText() const {
    return m_titleText;
}

void QuolWindow::addContent(QWidget *widget) {
    m_bodyLayout->addWidget(widget);
}

void QuolWindow::addContent(QLayout *layout) {
    m_bodyLayout->addLayout(layout);
}

void QuolWindow::attachConfigWindow(const QString &configPath, const QString &configTitle) {
    m_pluginConfigPath = configPath;

    if (m_configWindow) {
        m_configWindow->deleteLater();
    }

    const QString resolvedTitle = configTitle.isEmpty() ? (m_titleText + " Config") : configTitle;

    m_configWindow = new ConfigWindow(resolvedTitle, m_settings, configPath, this);
    connect(m_configWindow, &ConfigWindow::configSaved, this, [this](const QJsonObject &config) {
        if (m_onConfigSaved) {
            m_onConfigSaved(config);
        }

        const QJsonObject underscore = config.value(QStringLiteral("_")).toObject();
        const QJsonArray geometry = underscore.value(QStringLiteral("geometry")).toArray();
        if (geometry.size() >= 4) {
            const int gx = geometry.at(0).toInt(x());
            const int gy = geometry.at(1).toInt(y());
            const int gw = geometry.at(2).toInt(width());
            const int gh = geometry.at(3).toInt(height());

            m_autoHeightRequested = (gh <= 0);
            setGeometry(gx, gy, gw, (gh <= 0) ? autoHeightFromContent() : gh);
        }
    });

    m_titleBar->setConfigAction([this]() {
        const QRect screen = QGuiApplication::primaryScreen()->availableGeometry();
        const QSize sz = m_configWindow->size();
        m_configWindow->move(screen.center().x() - sz.width() / 2, screen.center().y() - sz.height() / 2);
        m_configWindow->show();
        m_configWindow->raise();
        m_configWindow->activateWindow();
    });

    if (!loadGeometryFromPluginConfig()) {
        saveGeometryToPluginConfig();
    }
}

void QuolWindow::setConfigSavedCallback(const std::function<void(const QJsonObject &)> &callback) {
    m_onConfigSaved = callback;
}

void QuolWindow::setGeometryPersistence(bool enabled) {
    m_persistGeometry = enabled;
}

bool QuolWindow::applyGeometryFromConfig() {
    loadGeometryFromPluginConfig();
    return true;
}

void QuolWindow::snapToGrid() {
    const int nx = qRound(static_cast<double>(pos().x()) / static_cast<double>(m_snapGrid)) * m_snapGrid;
    const int ny = qRound(static_cast<double>(pos().y()) / static_cast<double>(m_snapGrid)) * m_snapGrid;
    move(nx, ny);
    saveGeometry();
}

void QuolWindow::saveGeometry() {
    if (!m_persistGeometry) {
        return;
    }

    if (!saveGeometryToPluginConfig()) {
        m_settings->setWindowGeometry(m_titleText, x(), y(), width(), height());
    }
}

void QuolWindow::resizeEvent(QResizeEvent *event) {
    QWidget::resizeEvent(event);
    updateMask();
}

void QuolWindow::closeEvent(QCloseEvent *event) {
    if (m_configWindow) {
        m_configWindow->close();
    }
    QWidget::closeEvent(event);
}

void QuolWindow::showEvent(QShowEvent *event) {
    QWidget::showEvent(event);

    if (m_autoHeightRequested) {
        m_autoHeightRequested = false;
        resize(width(), autoHeightFromContent());
        saveGeometry();
    }
}

void QuolWindow::updateMask() {
    QPainterPath path;
    path.addRoundedRect(rect(), 6, 6);
    setMask(QRegion(path.toFillPolygon().toPolygon()));
}

void QuolWindow::loadGeometry(int defaultX, int defaultY, int defaultW, int defaultH) {
    if (!m_persistGeometry) {
        setGeometry(defaultX, defaultY, defaultW, defaultH);
        return;
    }

    const QJsonObject configs = m_settings->data().value(QStringLiteral("configs")).toObject();
    const QJsonObject windowCfg = configs.value(m_titleText).toObject();
    const QJsonArray geometry =
        windowCfg.value(QStringLiteral("_")).toObject().value(QStringLiteral("geometry")).toArray();

    if (geometry.size() >= 4) {
        setGeometry(
            geometry.at(0).toInt(defaultX),
            geometry.at(1).toInt(defaultY),
            geometry.at(2).toInt(defaultW),
            geometry.at(3).toInt(defaultH)
        );
        return;
    }

    setGeometry(defaultX, defaultY, defaultW, defaultH);
}

bool QuolWindow::loadGeometryFromPluginConfig() {
    if (m_pluginConfigPath.isEmpty()) {
        return false;
    }

    QFile file(m_pluginConfigPath);
    if (!file.open(QIODevice::ReadOnly | QIODevice::Text)) {
        return false;
    }
    const QJsonDocument doc = QJsonDocument::fromJson(file.readAll());
    file.close();

    QJsonObject root = doc.object();
    QJsonObject underscore = root.value(QStringLiteral("_")).toObject();
    const bool hasDefaultGeometry = underscore.value(QStringLiteral("default_geometry")).isArray()
                                    && underscore.value(QStringLiteral("default_geometry")).toArray().size() >= 4;
    const bool useDefaultPos = m_settings && m_settings->data().value(QStringLiteral("is_default_pos")).toBool(false);
    const QJsonArray defaultGeometry = underscore.value(QStringLiteral("default_geometry")).toArray();
    QJsonArray geometry = underscore.value(QStringLiteral("geometry")).toArray();

    bool configChanged = false;

    if (useDefaultPos && defaultGeometry.size() >= 4) {
        geometry = defaultGeometry;
        underscore.insert(QStringLiteral("geometry"), geometry);
        root.insert(QStringLiteral("_"), underscore);
        configChanged = true;
    }

    if (geometry.size() < 4) {
        if (defaultGeometry.size() >= 4) {
            geometry = defaultGeometry;
            underscore.insert(QStringLiteral("geometry"), geometry);
            root.insert(QStringLiteral("_"), underscore);
            configChanged = true;
        }
    }

    const int gx = geometry.at(0).toInt(x());
    const int gy = geometry.at(1).toInt(y());
    const int gw = geometry.at(2).toInt(width());
    const int gh = geometry.at(3).toInt(height());

    m_autoHeightRequested = (gh <= 0);

    setGeometry(gx, gy, gw, (gh <= 0) ? autoHeightFromContent() : gh);

    if (configChanged) {
        if (file.open(QIODevice::WriteOnly | QIODevice::Text | QIODevice::Truncate)) {
            file.write(QJsonDocument(root).toJson(QJsonDocument::Indented));
            file.close();
        }
    }

    if (!hasDefaultGeometry) {
        saveGeometryToPluginConfig();
    }

    return true;
}

bool QuolWindow::saveGeometryToPluginConfig() const {
    if (m_pluginConfigPath.isEmpty()) {
        return false;
    }

    QFile file(m_pluginConfigPath);
    QJsonObject root;

    if (file.open(QIODevice::ReadOnly | QIODevice::Text)) {
        const QJsonDocument doc = QJsonDocument::fromJson(file.readAll());
        root = doc.object();
        file.close();
    }

    QJsonObject underscore = root.value(QStringLiteral("_")).toObject();
    if (!underscore.value(QStringLiteral("default_geometry")).isArray()
        || underscore.value(QStringLiteral("default_geometry")).toArray().size() < 4) {
        underscore.insert(QStringLiteral("default_geometry"), QJsonArray{x(), y(), width(), 0});
    }
    underscore.insert(QStringLiteral("geometry"), QJsonArray{x(), y(), width(), height()});
    root.insert(QStringLiteral("_"), underscore);

    bool written = file.open(QIODevice::WriteOnly | QIODevice::Text | QIODevice::Truncate);
    file.write(QJsonDocument(root).toJson(QJsonDocument::Indented));
    file.close();
    return true;
}

int QuolWindow::autoHeightFromContent() const {
    const int hint = sizeHint().height();
    const int minHint = minimumSizeHint().height();
    const int current = height();
    const int preferred = qMax(hint, minHint);
    return (preferred > 0) ? preferred : qMax(1, current);
}

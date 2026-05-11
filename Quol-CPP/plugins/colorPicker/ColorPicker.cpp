#include "plugins/colorPicker/ColorPicker.hpp"

#include <QColor>
#include <QCursor>
#include <QGridLayout>
#include <QGuiApplication>
#include <QIcon>
#include <QJsonObject>
#include <QLabel>
#include <QPainter>
#include <QPen>
#include <QPixmap>
#include <QPushButton>
#include <QScreen>
#include <QTimer>
#include <QWidget>

// ---------------------------------------------------------------------------
QWidget *ColorPicker::createWidget(QWidget *parent) {
    auto *widget = new QWidget(parent);
    m_gridLayout = new QGridLayout(widget);
    m_gridLayout->setContentsMargins(4, 4, 4, 4);
    m_gridLayout->setSpacing(4);

    // Preview label (zoomed pixel grid, top-left)
    m_previewLabel = new QLabel(widget);
    m_previewLabel->setFixedSize(55, 55);
    m_previewLabel->setAlignment(Qt::AlignCenter);
    m_gridLayout->addWidget(m_previewLabel, 0, 0, 3, 1);

    // Hex value (selectable so user can copy)
    m_hexLabel = new QLabel(QStringLiteral("#------"), widget);
    m_hexLabel->setAlignment(Qt::AlignCenter);
    m_hexLabel->setTextInteractionFlags(Qt::TextSelectableByMouse);
    m_gridLayout->addWidget(m_hexLabel, 0, 1);

    // RGB value (selectable)
    m_rgbLabel = new QLabel(QStringLiteral("r, g, b"), widget);
    m_rgbLabel->setAlignment(Qt::AlignCenter);
    m_rgbLabel->setTextInteractionFlags(Qt::TextSelectableByMouse);
    m_gridLayout->addWidget(m_rgbLabel, 1, 1);

    // Pick button with eyedropper icon
    m_pickButton = new QPushButton(widget);
    m_pickButton->setCheckable(true);
    if (!m_pluginRootPath.isEmpty()) {
        m_pickButton->setIcon(QIcon(m_pluginRootPath + "/res/img/pick.svg"));
    }
    m_gridLayout->addWidget(m_pickButton, 2, 1);

    QObject::connect(m_pickButton, &QPushButton::clicked, this, &ColorPicker::togglePicking);

    // Screen scale factor
    if (QScreen *screen = QGuiApplication::primaryScreen())
        m_sf = screen->devicePixelRatio();

    // Update color once on creation so the preview isn't blank
    updateColor();

    return widget;
}

// ---------------------------------------------------------------------------
void ColorPicker::initialize(
    const QString &pluginRootPath, const QJsonObject &appSettings, const QJsonObject &pluginConfig
) {
    Q_UNUSED(appSettings)
    m_pluginRootPath = pluginRootPath;
    m_pluginConfig = pluginConfig;

    if (m_pickButton && !pluginRootPath.isEmpty())
        m_pickButton->setIcon(QIcon(pluginRootPath + "/res/img/pick.svg"));

    if (QScreen *screen = QGuiApplication::primaryScreen())
        m_sf = screen->devicePixelRatio();
}

void ColorPicker::onUpdateConfig(const QJsonObject &pluginConfig) {
    m_pluginConfig = pluginConfig;
}

void ColorPicker::shutdown() {
    stopPicking();
    m_previewLabel = nullptr;
    m_hexLabel = nullptr;
    m_rgbLabel = nullptr;
    m_pickButton = nullptr;
    m_gridLayout = nullptr;
}

// ---------------------------------------------------------------------------
void ColorPicker::togglePicking() {
    if (m_timer && m_timer->isActive()) {
        stopPicking();
        return;
    }

    // Start polling
    if (!m_timer) {
        m_timer = new QTimer(this);
        QObject::connect(m_timer, &QTimer::timeout, this, &ColorPicker::updateColor);
    }
    m_timer->start(100);

    if (m_pickButton) {
        m_pickButton->setText(QStringLiteral("Stop"));
        m_pickButton->setIcon(QIcon{});
        m_pickButton->setStyleSheet(QStringLiteral("background-color: #eee; color: #000;"));
        m_pickButton->setChecked(true);
    }
}

void ColorPicker::stopPicking() {
    if (m_timer)
        m_timer->stop();

    if (m_pickButton) {
        m_pickButton->setText(QString{});
        if (!m_pluginRootPath.isEmpty())
            m_pickButton->setIcon(QIcon(m_pluginRootPath + "/res/img/pick.svg"));
        m_pickButton->setStyleSheet(QString{});
        m_pickButton->setChecked(false);
    }
}

// ---------------------------------------------------------------------------
void ColorPicker::updateColor() {
    QScreen *screen = QGuiApplication::primaryScreen();
    if (!screen)
        return;

    const QPoint pos = QCursor::pos();
    const int ps = 5;  // pixel sample radius (5×5 area)

    // Grab a small region around the cursor (in physical pixels on HiDPI)
    const int x = pos.x() - ps / 2;
    const int y = pos.y() - ps / 2;

    QPixmap grabbed = screen->grabWindow(0, x, y, ps, ps);
    if (grabbed.isNull())
        return;

    QImage image = grabbed.toImage();
    if (image.isNull() || image.width() < 3 || image.height() < 3)
        return;

    // Scale up for the preview widget
    QPixmap scaled = QPixmap::fromImage(image).scaled(
        QSize(static_cast<int>(55 * m_sf), static_cast<int>(55 * m_sf)), Qt::IgnoreAspectRatio, Qt::FastTransformation
    );

    drawFrame(scaled);

    if (m_previewLabel)
        m_previewLabel->setPixmap(scaled);

    // Center pixel color
    const QColor center(image.pixel(ps / 2, ps / 2));

    if (m_hexLabel)
        m_hexLabel->setText(center.name());

    if (m_rgbLabel)
        m_rgbLabel->setText(
            QString::number(center.red()) + QStringLiteral(", ") + QString::number(center.green())
            + QStringLiteral(", ") + QString::number(center.blue())
        );
}

// ---------------------------------------------------------------------------
void ColorPicker::drawFrame(QPixmap &pixmap) {
    QPainter painter(&pixmap);
    if (!painter.isActive())
        return;

    const qreal sq = pixmap.width() / m_sf;
    const qreal cx = sq / 2.0;
    const qreal cy = sq / 2.0;

    QPen pen;
    pen.setColor(Qt::white);
    pen.setWidth(2);
    painter.setPen(pen);

    // Inner highlight box around centre pixel
    painter.drawRect(
        static_cast<int>(sq / 5.0 * 2),
        static_cast<int>(sq / 5.0 * 2),
        static_cast<int>(sq / 5.0 + 2),
        static_cast<int>(sq / 5.0 + 2)
    );
    // Outer border
    painter.drawRect(0, 0, static_cast<int>(sq), static_cast<int>(sq));

    pen.setWidth(1);
    painter.setPen(pen);

    const qreal b = sq / 10.0;
    // Cross-hair lines
    painter.drawLine(QPointF(cx, 0), QPointF(cx, cy - b - 1));
    painter.drawLine(QPointF(0, cy), QPointF(cx - b - 1, cy));
    painter.drawLine(QPointF(cx, sq), QPointF(cx, cy + b + 1));
    painter.drawLine(QPointF(sq, cy), QPointF(cy + b + 1, cy));

    painter.end();
}

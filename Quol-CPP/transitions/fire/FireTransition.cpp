#include "ui/transitions/ITransition.hpp"

#include <QAbstractAnimation>
#include <QImage>
#include <QPainter>
#include <QPixmap>
#include <QWidget>

#include <cmath>
#include <vector>

namespace {

static float hashF(int x, int y) {
    unsigned h = static_cast<unsigned>(x * 374761393 + y * 668265263);
    h = (h ^ (h >> 13)) * 1274126177u;
    h ^= (h >> 16);
    return float(h & 0x00FFFFFFu) / float(0x01000000u);
}
static float valueNoise(float x, float y) {
    int ix = static_cast<int>(std::floor(x)), iy = static_cast<int>(std::floor(y));
    float fx = x - float(ix), fy = y - float(iy);
    fx = fx * fx * (3.f - 2.f * fx);
    fy = fy * fy * (3.f - 2.f * fy);
    float a = hashF(ix, iy), b = hashF(ix + 1, iy), c = hashF(ix, iy + 1), d = hashF(ix + 1, iy + 1);
    return a + (b - a) * fx + (c - a) * fy + (a - b - c + d) * fx * fy;
}
static float fbm(float x, float y) {
    return valueNoise(x, y) * 0.5f + valueNoise(x * 2.f, y * 2.f) * 0.25f + valueNoise(x * 4.f, y * 4.f) * 0.125f;
}

static std::vector<float> buildThresholdMap(int W, int H) {
    std::vector<float> m(static_cast<size_t>(W * H));
    for (int row = 0; row < H; ++row) {
        for (int col = 0; col < W; ++col) {
            float nx = float(col) / float(W) - 1.5f;
            float ny = float(row) / float(H);
            m[static_cast<size_t>(row * W + col)] = nx + ny * 0.5f + 0.5f * fbm(nx * 15.1f, ny * 15.1f);
        }
    }
    return m;
}

static QImage burnFrame(const QImage &src32, const std::vector<float> &thresh, float t) {
    const int W = src32.width(), H = src32.height();
    QImage out(W, H, QImage::Format_ARGB32_Premultiplied);
    const float ctime = t * 2.0f;
    for (int row = 0; row < H; ++row) {
        QRgb *dst = reinterpret_cast<QRgb *>(out.scanLine(row));
        const QRgb *src = reinterpret_cast<const QRgb *>(src32.constScanLine(row));
        for (int col = 0; col < W; ++col) {
            const float d = thresh[static_cast<size_t>(row * W + col)] + ctime;
            if (d > 0.5f) {
                dst[col] = 0;
            } else if (d > 0.35f) {
                const float e = (d - 0.35f) / 0.15f;
                const int alpha = static_cast<int>(255.f * (1.f - e));
                const float glow = (1.f - e) * 0.85f;
                int r = std::min(255, qRed(src[col]) + static_cast<int>(glow * 220.f));
                int g = std::min(255, qGreen(src[col]) + static_cast<int>(glow * 80.f));
                int b = qBlue(src[col]);
                dst[col] = qRgba(r * alpha / 255, g * alpha / 255, b * alpha / 255, alpha);
            } else {
                dst[col] = src[col];
            }
        }
    }
    return out;
}

class FireOverlayWindow : public QWidget {
public:
    explicit FireOverlayWindow() {
        setWindowFlags(Qt::FramelessWindowHint | Qt::Tool | Qt::WindowStaysOnTopHint);
        setAttribute(Qt::WA_TranslucentBackground);
        setAttribute(Qt::WA_ShowWithoutActivating);
        setAttribute(Qt::WA_NoSystemBackground);
    }
    void setFrame(const QImage &frame) {
        m_frame = frame;
        update();
    }

protected:
    void paintEvent(QPaintEvent *) override {
        if (m_frame.isNull())
            return;
        QPainter p(this);
        p.drawImage(0, 0, m_frame);
    }

private:
    QImage m_frame;
};

class FireShaderAnimation final : public QAbstractAnimation {
public:
    FireShaderAnimation(QWidget *target, const QPoint &savedPos, bool hidePhase, int durationMs = 500)
        : m_target(target), m_savedPos(savedPos), m_hidePhase(hidePhase), m_duration(durationMs) {
    }

    int duration() const override {
        return m_duration;
    }

protected:
    void updateCurrentTime(int currentTime) override {
        if (!m_overlay || m_source.isNull() || m_thresh.empty())
            return;
        const float t = float(currentTime) / float(qMax(1, m_duration));
        m_overlay->setFrame(burnFrame(m_source, m_thresh, m_hidePhase ? t : 1.f - t));
    }

    void updateState(QAbstractAnimation::State newState, QAbstractAnimation::State oldState) override {
        QAbstractAnimation::updateState(newState, oldState);
        if (newState == Running && oldState == Stopped)
            begin();
        if (newState == Stopped && oldState == Running)
            end();
    }

private:
    static QImage captureWindow(QWidget *w) {
        QPixmap pm(w->size());
        pm.fill(Qt::transparent);
        w->render(&pm, QPoint(0, 0));
        return pm.toImage().convertToFormat(QImage::Format_ARGB32_Premultiplied);
    }

    void begin() {
        if (!m_target)
            return;
        const QRect overlayGeom(m_savedPos, m_target->size());
        if (!m_hidePhase) {
            // Render offscreen to capture content without flashing on-screen
            m_target->move(-32000, -32000);
            m_target->show();
            m_target->repaint();
        }
        m_source = captureWindow(m_target);
        m_target->hide();
        if (m_hidePhase)
            m_target->move(m_savedPos);  // restore pos so show works after
        if (m_source.isNull())
            return;
        m_thresh = buildThresholdMap(m_source.width(), m_source.height());
        m_overlay = new FireOverlayWindow();
        m_overlay->setGeometry(overlayGeom);
        m_overlay->setFrame(burnFrame(m_source, m_thresh, m_hidePhase ? 0.f : 1.f));
        m_overlay->show();
        m_overlay->raise();
    }

    void end() {
        if (m_overlay) {
            m_overlay->close();
            m_overlay->deleteLater();
            m_overlay = nullptr;
        }
        if (!m_target)
            return;
        m_target->setWindowOpacity(1.0);
        if (m_hidePhase) {
            m_target->hide();
        } else {
            m_target->move(m_savedPos);
            m_target->show();
            m_target->raise();
        }
    }

    QWidget *m_target = nullptr;
    QPoint m_savedPos;
    bool m_hidePhase;
    int m_duration;
    QImage m_source;
    std::vector<float> m_thresh;
    FireOverlayWindow *m_overlay = nullptr;
};

class FireTransition final : public ITransition {
public:
    QString name() const override {
        return QStringLiteral("fire");
    }
    QAbstractAnimation *createHideAnimation(QWidget *w, const QPoint &savedPos) const override {
        return new FireShaderAnimation(w, savedPos, true);
    }
    QAbstractAnimation *createShowAnimation(QWidget *w, const QPoint &savedPos) const override {
        return new FireShaderAnimation(w, savedPos, false);
    }
};

}  // namespace

extern "C" Q_DECL_EXPORT ITransition *createTransition() {
    return new FireTransition();
}

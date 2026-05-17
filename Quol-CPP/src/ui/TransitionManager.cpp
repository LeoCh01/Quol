#include "ui/TransitionManager.hpp"

#include "ui/transitions/ITransition.hpp"

#include <QAbstractAnimation>
#include <QCoreApplication>
#include <QGuiApplication>
#include <QLibrary>
#include <QParallelAnimationGroup>
#include <QPropertyAnimation>
#include <QRandomGenerator>
#include <QScreen>
#include <QWidget>

namespace {
class NoneTransition final : public ITransition {
public:
    QString name() const override {
        return QStringLiteral("none");
    }

    QAbstractAnimation *createHideAnimation(QWidget *, const QPoint &) const override {
        return nullptr;
    }

    QAbstractAnimation *createShowAnimation(QWidget *w, const QPoint &savedPos) const override {
        w->move(savedPos);
        w->show();
        return nullptr;
    }
};

class FadeTransition final : public ITransition {
public:
    explicit FadeTransition(int durationMs = 200) : m_duration(durationMs) {
    }

    QString name() const override {
        return QStringLiteral("fade");
    }

    QAbstractAnimation *createHideAnimation(QWidget *w, const QPoint &) const override {
        auto *anim = new QPropertyAnimation(w, "windowOpacity");
        anim->setDuration(m_duration);
        anim->setStartValue(1.0);
        anim->setEndValue(0.0);
        return anim;
    }

    QAbstractAnimation *createShowAnimation(QWidget *w, const QPoint &savedPos) const override {
        w->move(savedPos);
        w->setWindowOpacity(0.0);
        w->show();

        auto *anim = new QPropertyAnimation(w, "windowOpacity");
        anim->setDuration(m_duration);
        anim->setStartValue(0.0);
        anim->setEndValue(1.0);
        return anim;
    }

private:
    int m_duration;
};

enum class SlideDirection { Left, Right, Up, Down };

class SlideTransition final : public ITransition {
public:
    explicit SlideTransition(SlideDirection dir, int durationMs = 200) : m_dir(dir), m_duration(durationMs) {
    }

    QString name() const override {
        switch (m_dir) {
            case SlideDirection::Left:
                return QStringLiteral("slide-left");
            case SlideDirection::Right:
                return QStringLiteral("slide-right");
            case SlideDirection::Up:
                return QStringLiteral("slide-up");
            default:
                return QStringLiteral("slide-down");
        }
    }

    QAbstractAnimation *createHideAnimation(QWidget *w, const QPoint &savedPos) const override {
        auto *anim = new QPropertyAnimation(w, "pos");
        anim->setDuration(m_duration);
        anim->setStartValue(w->pos());
        anim->setEndValue(offScreenPos(w, savedPos));
        return anim;
    }

    QAbstractAnimation *createShowAnimation(QWidget *w, const QPoint &savedPos) const override {
        w->show();
        auto *anim = new QPropertyAnimation(w, "pos");
        anim->setDuration(m_duration);
        anim->setStartValue(w->pos());
        anim->setEndValue(savedPos);
        return anim;
    }

private:
    QPoint offScreenPos(QWidget *w, const QPoint &from) const {
        QScreen *screen = QGuiApplication::primaryScreen();
        const QRect r = screen ? screen->availableGeometry() : QRect(0, 0, 1920, 1080);
        switch (m_dir) {
            case SlideDirection::Left:
                return {r.left() - w->width() - 30, from.y()};
            case SlideDirection::Right:
                return {r.right() + 31, from.y()};
            case SlideDirection::Up:
                return {from.x(), r.top() - w->height() - 30};
            default:
                return {from.x(), r.bottom() + 31};
        }
    }

    SlideDirection m_dir;
    int m_duration;
};

class RandTransition final : public ITransition {
public:
    explicit RandTransition(int durationMs = 200) : m_duration(durationMs) {
    }

    QString name() const override {
        return QStringLiteral("rand");
    }

    QAbstractAnimation *createHideAnimation(QWidget *w, const QPoint &savedPos) const override {
        const QPoint target = randomOffScreenPos(w, savedPos);

        auto *posAnim = new QPropertyAnimation(w, "pos");
        posAnim->setDuration(m_duration);
        posAnim->setStartValue(w->pos());
        posAnim->setEndValue(target);

        auto *opAnim = new QPropertyAnimation(w, "windowOpacity");
        opAnim->setDuration(m_duration);
        opAnim->setStartValue(1.0);
        opAnim->setEndValue(0.0);

        auto *group = new QParallelAnimationGroup;
        group->addAnimation(posAnim);
        group->addAnimation(opAnim);
        return group;
    }

    QAbstractAnimation *createShowAnimation(QWidget *w, const QPoint &savedPos) const override {
        w->setWindowOpacity(0.0);
        w->show();

        auto *posAnim = new QPropertyAnimation(w, "pos");
        posAnim->setDuration(m_duration);
        posAnim->setStartValue(w->pos());
        posAnim->setEndValue(savedPos);

        auto *opAnim = new QPropertyAnimation(w, "windowOpacity");
        opAnim->setDuration(m_duration);
        opAnim->setStartValue(0.0);
        opAnim->setEndValue(1.0);

        auto *group = new QParallelAnimationGroup;
        group->addAnimation(posAnim);
        group->addAnimation(opAnim);
        return group;
    }

private:
    QPoint randomOffScreenPos(QWidget *w, const QPoint &from) const {
        QScreen *screen = QGuiApplication::primaryScreen();
        const QRect r = screen ? screen->availableGeometry() : QRect(0, 0, 1920, 1080);
        switch (QRandomGenerator::global()->bounded(4)) {
            case 0:
                return {r.left() - w->width() - 30, from.y()};
            case 1:
                return {r.right() + 31, from.y()};
            case 2:
                return {from.x(), r.top() - w->height() - 30};
            default:
                return {from.x(), r.bottom() + 31};
        }
    }

    int m_duration;
};
}  // namespace

TransitionManager::TransitionManager(const QString &type, QObject *parent)
    : QObject(parent), m_searchPath(QCoreApplication::applicationDirPath() + "/transitions/") {
    registerBuiltins();
    setType(type);
}

TransitionManager::~TransitionManager() {
    for (auto *t : m_ownedTransitions)
        delete t;
    for (auto *lib : m_libraries) {
        lib->unload();
        lib->deleteLater();
    }
}

void TransitionManager::registerBuiltins() {
    auto reg = [this](ITransition *t) {
        m_ownedTransitions.emplace_back(t);
        m_registry.insert(t->name(), t);
    };
    reg(new NoneTransition());
    reg(new FadeTransition());
    reg(new SlideTransition(SlideDirection::Left));
    reg(new SlideTransition(SlideDirection::Right));
    reg(new SlideTransition(SlideDirection::Up));
    reg(new SlideTransition(SlideDirection::Down));
    reg(new RandTransition());
}

void TransitionManager::setType(const QString &type) {
    const QString normalized = type.trimmed().toLower();
    m_type = normalized.isEmpty() ? QStringLiteral("none") : normalized;
}

void TransitionManager::setSearchPath(const QString &path) {
    m_searchPath = path;
}

QStringList TransitionManager::registeredNames() const {
    return m_registry.keys();
}

void TransitionManager::addWindow(QWidget *window) {
    m_windows.append(window);
    m_savedPositions.append(window->pos());
}

bool TransitionManager::isHidden() const {
    return m_hidden;
}

void TransitionManager::toggleAll() {
    if (!m_hidden) {
        hideAll();
        m_hidden = true;
    } else {
        showAll();
        m_hidden = false;
    }
}

void TransitionManager::hideAll() {
    ITransition *t = resolve(m_type);
    for (int i = 0; i < m_windows.size(); ++i) {
        QWidget *w = m_windows[i];
        if (w->isVisible())
            m_savedPositions[i] = w->pos();
        doHide(w, i, t);
    }
}

void TransitionManager::showAll() {
    ITransition *t = resolve(m_type);
    for (int i = 0; i < m_windows.size(); ++i)
        doShow(m_windows[i], i, t);
}

void TransitionManager::doHide(QWidget *w, int idx, ITransition *t) {
    stopAnimation(w);
    if (!w->isVisible())
        return;

    QAbstractAnimation *anim = t->createHideAnimation(w, m_savedPositions[idx]);
    if (!anim) {
        w->hide();
        w->setWindowOpacity(1.0);
        return;
    }

    trackAnimation(w, anim);
    QObject::connect(anim, &QAbstractAnimation::finished, this, [this, w, anim]() {
        if (m_activeAnimations.value(w) != anim)
            return;
        m_activeAnimations.remove(w);
        w->hide();
        w->setWindowOpacity(1.0);
        anim->deleteLater();
    });
    anim->start();
}

void TransitionManager::doShow(QWidget *w, int idx, ITransition *t) {
    stopAnimation(w);

    QAbstractAnimation *anim = t->createShowAnimation(w, m_savedPositions[idx]);
    if (!anim)
        return;

    trackAnimation(w, anim);
    QObject::connect(anim, &QAbstractAnimation::finished, this, [this, w, anim]() {
        if (m_activeAnimations.value(w) != anim)
            return;
        m_activeAnimations.remove(w);
        anim->deleteLater();
    });
    anim->start();
}

ITransition *TransitionManager::resolve(const QString &type) {
    if (m_registry.contains(type))
        return m_registry.value(type);

    // Not in registry — try loading a DLL from the transitions search path
    ITransition *dllTransition = tryLoadDll(type);
    if (dllTransition)
        return dllTransition;

    // Fallback to instant
    return m_registry.value(QStringLiteral("none"));
}

ITransition *TransitionManager::tryLoadDll(const QString &name) {
#ifdef Q_OS_WIN
    const QString ext = QStringLiteral(".dll");
#elif defined(Q_OS_MAC)
    const QString ext = QStringLiteral(".dylib");
#else
    const QString ext = QStringLiteral(".so");
#endif

    const QString path = m_searchPath + name + ext;
    auto *lib = new QLibrary(path, this);
    if (!lib->load()) {
        lib->deleteLater();
        return nullptr;
    }

    using CreateFn = ITransition *(*) ();
    auto createFn = reinterpret_cast<CreateFn>(lib->resolve("createTransition"));
    if (!createFn) {
        lib->unload();
        lib->deleteLater();
        return nullptr;
    }

    ITransition *t = createFn();
    if (!t) {
        lib->unload();
        lib->deleteLater();
        return nullptr;
    }

    m_ownedTransitions.emplace_back(t);
    m_registry.insert(t->name(), t);
    m_libraries.append(lib);
    return t;
}

void TransitionManager::trackAnimation(QWidget *w, QAbstractAnimation *animation) {
    m_activeAnimations.insert(w, animation);
}

void TransitionManager::stopAnimation(QWidget *w) {
    if (!m_activeAnimations.contains(w))
        return;

    QAbstractAnimation *animation = m_activeAnimations.take(w);
    if (!animation)
        return;

    animation->stop();
    animation->deleteLater();
}

#include "plugins/example/lib/adder.hpp"

#include <QJsonArray>

namespace examplelib {
QString selectedArrayOption(const QJsonValue &value) {
    if (!value.isArray()) {
        return {};
    }

    const QJsonArray arr = value.toArray();
    if (arr.size() != 2 || !arr.at(0).isArray()) {
        return {};
    }

    const QJsonArray options = arr.at(0).toArray();
    const int index = arr.at(1).toInt(-1);
    if (index < 0 || index >= options.size()) {
        return {};
    }

    return options.at(index).toString();
}

QString calculateFromConfig(const QJsonObject &config) {
    const int a = config.value("a").toInt(0);
    const int b = config.value("b").toInt(0);
    const QString op = selectedArrayOption(config.value("op"));

    if (op == "+") {
        return QString("%1 + %2 = %3").arg(a).arg(b).arg(a + b);
    }
    if (op == "-") {
        return QString("%1 - %2 = %3").arg(a).arg(b).arg(a - b);
    }
    if (op == "*") {
        return QString("%1 * %2 = %3").arg(a).arg(b).arg(a * b);
    }
    if (op == "/") {
        if (b == 0) {
            return QString("%1 / %2 = undefined").arg(a).arg(b);
        }
        return QString("%1 / %2 = %3").arg(a).arg(b).arg(static_cast<double>(a) / static_cast<double>(b));
    }

    return QString("a=%1, b=%2, op=(invalid)").arg(a).arg(b);
}

QString nestedNoteLine(const QJsonObject &config) {
    const QJsonObject nested = config.value("nested").toObject();
    const QString note = nested.value("note").toString();

    return QString("nested.note=%1").arg(note);
}

QString nestedEnabledLine(const QJsonObject &config) {
    const QJsonObject nested = config.value("nested").toObject();
    const bool enabled = nested.value("enabled").toBool(false);

    return QString("nested.enabled=%1").arg(enabled ? "true" : "false");
}

QString nestedModeLine(const QJsonObject &config) {
    const QJsonObject nested = config.value("nested").toObject();
    const QString mode = selectedArrayOption(nested.value("mode"));

    return QString("nested.mode=%1").arg(mode);
}

QString nestedInnerLabelLine(const QJsonObject &config) {
    const QJsonObject nested = config.value("nested").toObject();
    const QJsonObject inner = nested.value("inner").toObject();
    const QString label = inner.value("label").toString();

    return QString("nested.inner.label=%1").arg(label);
}

QString nestedInnerChoiceLine(const QJsonObject &config) {
    const QJsonObject nested = config.value("nested").toObject();
    const QJsonObject inner = nested.value("inner").toObject();
    const QString choice = selectedArrayOption(inner.value("choice"));

    return QString("nested.inner.choice=%1").arg(choice);
}
}  // namespace examplelib

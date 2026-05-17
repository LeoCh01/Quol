#pragma once

#include <QDialog>
#include <QList>
#include <QPair>
#include <QString>

class QLineEdit;
class QPushButton;
class QScrollArea;
class QVBoxLayout;
class QWidget;

// Dialog for creating / editing a mapping group.
// Shows a name field and a scrollable list of src → dst key-pair rows.
class KeymapGroupDialog : public QDialog {
    Q_OBJECT
public:
    explicit KeymapGroupDialog(QWidget *parent, const QString &name, const QList<QPair<QString, QString>> &mappings);

    // Returns the current name and list of (src, dst) pairs.
    QString groupName() const;
    QList<QPair<QString, QString>> mappings() const;

private slots:
    void addRow(const QString &src = {}, const QString &dst = {});
    void removeRow(QWidget *row);

private:
    QLineEdit *m_nameEdit = nullptr;
    QVBoxLayout *m_rowsLayout = nullptr;
    QWidget *m_rowsContainer = nullptr;
    QScrollArea *m_scrollArea = nullptr;

    QList<QWidget *> m_rows;
};

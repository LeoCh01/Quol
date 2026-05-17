#include "plugins/keymap/lib/KeymapGroupDialog.hpp"

#include <QColor>
#include <QDialogButtonBox>
#include <QHBoxLayout>
#include <QLabel>
#include <QLineEdit>
#include <QPalette>
#include <QPushButton>
#include <QScrollArea>
#include <QVBoxLayout>
#include <QWidget>

KeymapGroupDialog::KeymapGroupDialog(
    QWidget *parent, const QString &name, const QList<QPair<QString, QString>> &mappings
)
    : QDialog(parent) {
    setWindowTitle(name.isEmpty() ? "New Mapping Group" : "Edit: " + name);
    setMinimumWidth(340);

    auto *mainLayout = new QVBoxLayout(this);
    mainLayout->setContentsMargins(8, 8, 8, 8);
    mainLayout->setSpacing(6);

    // --- Name row ---
    auto *nameRow = new QHBoxLayout();
    nameRow->addWidget(new QLabel("Group name:", this));
    m_nameEdit = new QLineEdit(name, this);
    nameRow->addWidget(m_nameEdit);
    mainLayout->addLayout(nameRow);

    // --- Header ---
    auto *header = new QHBoxLayout();
    auto *srcLbl = new QLabel("Source key", this);
    srcLbl->setFixedWidth(130);
    auto *dstLbl = new QLabel("Target key", this);
    dstLbl->setFixedWidth(130);
    header->addWidget(srcLbl);
    header->addWidget(new QLabel("→", this));
    header->addWidget(dstLbl);
    header->addStretch();
    mainLayout->addLayout(header);

    // --- Scrollable rows ---
    m_rowsContainer = new QWidget(this);
    m_rowsLayout = new QVBoxLayout(m_rowsContainer);
    m_rowsLayout->setContentsMargins(0, 0, 0, 0);
    m_rowsLayout->setSpacing(3);
    m_rowsLayout->setAlignment(Qt::AlignTop);

    m_scrollArea = new QScrollArea(this);
    m_scrollArea->setWidget(m_rowsContainer);
    m_scrollArea->setWidgetResizable(true);
    m_scrollArea->setMinimumHeight(160);
    m_scrollArea->setMaximumHeight(300);
    // Force viewport background — QSS alone doesn't reach the viewport widget
    m_scrollArea->viewport()->setAutoFillBackground(true);
    QPalette vp = m_scrollArea->viewport()->palette();
    vp.setColor(QPalette::Window, QColor(0x2e, 0x2e, 0x2e));
    m_scrollArea->viewport()->setPalette(vp);
    mainLayout->addWidget(m_scrollArea);

    // Populate existing mappings
    for (const auto &pair : mappings)
        addRow(pair.first, pair.second);

    // --- Add row button ---
    auto *addBtn = new QPushButton("+ Add Mapping", this);
    connect(addBtn, &QPushButton::clicked, this, [this]() { addRow(); });
    mainLayout->addWidget(addBtn);

    // --- OK / Cancel ---
    auto *buttons = new QDialogButtonBox(QDialogButtonBox::Ok | QDialogButtonBox::Cancel, this);
    connect(buttons, &QDialogButtonBox::accepted, this, &QDialog::accept);
    connect(buttons, &QDialogButtonBox::rejected, this, &QDialog::reject);
    mainLayout->addWidget(buttons);
}

QString KeymapGroupDialog::groupName() const {
    return m_nameEdit->text().trimmed();
}

QList<QPair<QString, QString>> KeymapGroupDialog::mappings() const {
    QList<QPair<QString, QString>> result;
    for (auto *row : m_rows) {
        auto *srcEdit = row->findChild<QLineEdit *>("src");
        auto *dstEdit = row->findChild<QLineEdit *>("dst");
        if (!srcEdit || !dstEdit)
            continue;
        const QString src = srcEdit->text().trimmed().toLower();
        const QString dst = dstEdit->text().trimmed().toLower();
        if (!src.isEmpty() && !dst.isEmpty())
            result.append({src, dst});
    }
    return result;
}

void KeymapGroupDialog::addRow(const QString &src, const QString &dst) {
    auto *row = new QWidget(m_rowsContainer);
    auto *hl = new QHBoxLayout(row);
    hl->setContentsMargins(0, 0, 0, 0);
    hl->setSpacing(4);

    auto *srcEdit = new QLineEdit(src, row);
    srcEdit->setObjectName("src");
    srcEdit->setPlaceholderText("e.g. caps");
    srcEdit->setFixedWidth(120);

    auto *arrow = new QLabel("→", row);
    arrow->setFixedWidth(16);

    auto *dstEdit = new QLineEdit(dst, row);
    dstEdit->setObjectName("dst");
    dstEdit->setPlaceholderText("e.g. ctrl");
    dstEdit->setFixedWidth(120);

    auto *delBtn = new QPushButton("✖", row);
    delBtn->setFixedSize(22, 22);
    connect(delBtn, &QPushButton::clicked, this, [this, row]() { removeRow(row); });

    hl->addWidget(srcEdit);
    hl->addWidget(arrow);
    hl->addWidget(dstEdit);
    hl->addWidget(delBtn);
    hl->addStretch();

    m_rowsLayout->addWidget(row);
    m_rows.append(row);
    row->show();
}

void KeymapGroupDialog::removeRow(QWidget *row) {
    m_rows.removeOne(row);
    m_rowsLayout->removeWidget(row);
    row->deleteLater();
}

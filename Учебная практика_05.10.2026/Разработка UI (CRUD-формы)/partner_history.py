from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton,
    QLabel, QHeaderView, QMessageBox
)
import db


class PartnerHistoryWindow(QWidget):
    def __init__(self, partner_id: int, parent_window=None):
        super().__init__()
        self.partner_id = partner_id
        self.parent_window = parent_window
        self.setWindowTitle("История продаж")
        self.setMinimumSize(600, 400)
        self._build_ui()
        self._load_history()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("История реализации")
        title.setStyleSheet("font-size: 15px; font-weight: bold;")
        layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Товар", "Дата", "Количество"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)

        buttons = QHBoxLayout()
        btn_back = QPushButton("← Назад")
        btn_back.clicked.connect(self.close)
        buttons.addWidget(btn_back)
        buttons.addStretch()
        layout.addLayout(buttons)

    def _load_history(self):
        try:
            rows = db.fetch_sales_history(self.partner_id)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка подключения к БД",
                f"Не удалось загрузить историю продаж.\n\n"
                f"Проверьте:\n"
                f"1. Запущен ли PostgreSQL\n"
                f"2. Существует ли база данных partners_db\n\n"
                f"Подробности: {e}")
            return
        self.table.setRowCount(len(rows))
        for i, (product_name, sale_date, quantity) in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(product_name or ""))
            self.table.setItem(i, 1, QTableWidgetItem(str(sale_date)))
            self.table.setItem(i, 2, QTableWidgetItem(str(quantity)))
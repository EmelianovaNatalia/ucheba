from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton,
    QLabel, QHeaderView, QMessageBox
)
from PyQt5.QtCore import Qt
import db


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Управление партнёрами")
        self.setMinimumSize(900, 600)
        self._build_ui()
        self.load_partners()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QHBoxLayout()
        logo = QLabel("🏢 МастерПол")
        logo.setStyleSheet("font-size: 22px; font-weight: bold; color: #4a235a;")
        header.addWidget(logo)
        header.addStretch()
        layout.addLayout(header)

        title = QLabel("Партнёры")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Тип", "Наименование", "Телефон", "Рейтинг"]
        )
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.doubleClicked.connect(self._on_edit)
        layout.addWidget(self.table)

        buttons = QHBoxLayout()
        btn_add = QPushButton("Добавить партнёра")
        btn_add.setStyleSheet("background-color: #4a235a; color: white; padding: 8px 16px;")
        btn_add.clicked.connect(self._on_add)
        btn_history = QPushButton("История продаж")
        btn_history.setStyleSheet("padding: 8px 16px;")
        btn_history.clicked.connect(self._on_history)
        buttons.addWidget(btn_add)
        buttons.addWidget(btn_history)
        buttons.addStretch()
        layout.addLayout(buttons)

    def load_partners(self):
        try:
            rows = db.fetch_partners()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка подключения к БД",
                f"Не удалось загрузить список партнёров.\n\n"
                f"Проверьте:\n"
                f"1. Запущен ли PostgreSQL\n"
                f"2. Существует ли база данных partners_db\n\n"
                f"Подробности: {e}")
            return
        self.table.setRowCount(len(rows))
        for i, (pid, ptype, name, phone, rating) in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(str(pid)))
            self.table.setItem(i, 1, QTableWidgetItem(ptype or ""))
            self.table.setItem(i, 2, QTableWidgetItem(name or ""))
            self.table.setItem(i, 3, QTableWidgetItem(phone or ""))
            self.table.setItem(i, 4, QTableWidgetItem(str(rating or 0)))

    def _selected_partner_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        # Читаем partner_id из скрытой первой колонки таблицы
        return int(self.table.item(row, 0).text())

    def _on_add(self):
        from partner_edit import PartnerEditWindow
        self.edit_win = PartnerEditWindow(parent_window=self)
        self.edit_win.show()

    def _on_edit(self):
        pid = self._selected_partner_id()
        if pid is None:
            return
        from partner_edit import PartnerEditWindow
        # Передаём partner_id чтобы форма загрузила существующие данные
        self.edit_win = PartnerEditWindow(partner_id=pid, parent_window=self)
        self.edit_win.show()

    def _on_history(self):
        pid = self._selected_partner_id()
        if pid is None:
            QMessageBox.information(self, "Выберите партнёра",
                "Пожалуйста, выберите партнёра в таблице.")
            return
        from partner_history import PartnerHistoryWindow
        # Передаём partner_id чтобы окно истории показало продажи конкретного партнёра
        self.history_win = PartnerHistoryWindow(partner_id=pid, parent_window=self)
        self.history_win.show()
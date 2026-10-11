from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QSpinBox, QPushButton,
    QLabel, QMessageBox
)
from PyQt5.QtCore import Qt
import db


class PartnerEditWindow(QWidget):
    def __init__(self, partner_id=None, parent_window=None):
        super().__init__()
        self.partner_id = partner_id
        self.parent_window = parent_window
        self.setWindowTitle("Добавить партнёра" if partner_id is None else "Редактировать партнёра")
        self.setMinimumWidth(500)
        self._build_ui()
        self._load_types()
        if partner_id is not None:
            self._load_partner()
        # Сохраняем исходное состояние полей для сравнения при выходе
        self._initial_state = self._get_state()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("Редактирование партнёра" if self.partner_id else "Новый партнёр")
        title.setStyleSheet("font-size: 15px; font-weight: bold;")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("ООО Ромашка")
        form.addRow("Наименование:", self.name_edit)

        self.type_combo = QComboBox()
        form.addRow("Тип:", self.type_combo)

        self.inn_edit = QLineEdit()
        self.inn_edit.setPlaceholderText("XXXXXXXXXXXX (10 или 12 цифр)")
        self.inn_edit.setMaxLength(12)
        form.addRow("ИНН:", self.inn_edit)

        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("example@mail.ru")
        form.addRow("Email:", self.email_edit)

        self.director_edit = QLineEdit()
        self.director_edit.setPlaceholderText("Иванов Иван Иванович")
        form.addRow("Директор:", self.director_edit)

        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText("+7 (XXX) XXX-XX-XX")
        form.addRow("Телефон:", self.phone_edit)

        self.address_edit = QLineEdit()
        self.address_edit.setPlaceholderText("г. Москва, ул. Примерная, д. 1")
        form.addRow("Адрес:", self.address_edit)

        self.rating_spin = QSpinBox()
        self.rating_spin.setMinimum(0)
        self.rating_spin.setMaximum(10)
        form.addRow("Рейтинг:", self.rating_spin)

        layout.addLayout(form)

        buttons = QHBoxLayout()
        btn_back = QPushButton("← Назад")
        btn_back.clicked.connect(self._on_back)
        btn_save = QPushButton("Сохранить")
        btn_save.setStyleSheet("background-color: #4a235a; color: white; padding: 8px 16px;")
        btn_save.clicked.connect(self._on_save)
        buttons.addWidget(btn_back)
        buttons.addStretch()
        buttons.addWidget(btn_save)
        layout.addLayout(buttons)

    def _load_types(self):
        try:
            self.types = db.fetch_partner_types()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка подключения к БД",
                f"Не удалось загрузить типы партнёров.\n\n"
                f"Проверьте:\n"
                f"1. Запущен ли PostgreSQL\n"
                f"2. Существует ли база данных partners_db\n\n"
                f"Подробности: {e}")
            self.types = []
            return
        self.type_combo.clear()
        for tid, tname in self.types:
            self.type_combo.addItem(tname, tid)

    def _load_partner(self):
        try:
            row = db.fetch_partner(self.partner_id)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка подключения к БД",
                f"Не удалось загрузить данные партнёра.\n\n"
                f"Проверьте:\n"
                f"1. Запущен ли PostgreSQL\n"
                f"2. Существует ли база данных partners_db\n\n"
                f"Подробности: {e}")
            return
        if row is None:
            return
        _, type_id, name, inn, email, director, phone, address, rating = row
        self.name_edit.setText(name or "")
        self.inn_edit.setText(inn or "")
        self.email_edit.setText(email or "")
        self.director_edit.setText(director or "")
        self.phone_edit.setText(phone or "")
        self.address_edit.setText(address or "")
        self.rating_spin.setValue(rating or 0)
        # Выбираем тип в ComboBox по совпадению partner_type_id
        for i, (tid, _) in enumerate(self.types):
            if tid == type_id:
                self.type_combo.setCurrentIndex(i)
                break

    def _get_state(self) -> tuple:
        """Возвращает текущее состояние полей для сравнения с исходным."""
        return (
            self.name_edit.text(),
            self.type_combo.currentIndex(),
            self.inn_edit.text(),
            self.email_edit.text(),
            self.director_edit.text(),
            self.phone_edit.text(),
            self.address_edit.text(),
            self.rating_spin.value(),
        )

    def _on_back(self):
        # Предупреждаем пользователя если данные были изменены
        if self._get_state() != self._initial_state:
            reply = QMessageBox.warning(
                self, "Несохранённые изменения",
                "Вы изменили данные. При выходе все изменения будут потеряны безвозвратно.\n\n"
                "Всё равно выйти?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return
        self.close()

    def _on_save(self):
        name = self.name_edit.text().strip()
        inn = self.inn_edit.text().strip()
        email = self.email_edit.text().strip()
        if not name or not inn or not email:
            QMessageBox.warning(self, "Ошибка ввода",
                "Поля «Наименование», «ИНН» и «Email» обязательны для заполнения.\n\n"
                "Заполните все обязательные поля и повторите попытку.")
            return
        # Все поля передаются параметризованно через psycopg2 — SQL-инъекции исключены
        data = {
            "partner_type_id": self.type_combo.currentData(),
            "partner_name": name,
            "inn": inn,
            "email": email,
            "director": self.director_edit.text().strip() or None,
            "phone": self.phone_edit.text().strip() or None,
            "address": self.address_edit.text().strip() or None,
            "rating": self.rating_spin.value(),
        }
        try:
            db.save_partner(data, self.partner_id)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка сохранения",
                f"Не удалось сохранить данные партнёра.\n\n"
                f"Проверьте:\n"
                f"1. Уникальность ИНН и Email\n"
                f"2. Доступность базы данных\n\n"
                f"Подробности: {e}")
            return
        if self.parent_window is not None:
            # Обновляем таблицу на главном окне после сохранения
            self.parent_window.load_partners()
        self.close()
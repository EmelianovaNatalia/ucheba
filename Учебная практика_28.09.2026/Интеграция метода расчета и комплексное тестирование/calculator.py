# calculator.py
# Задание 3: Интеграция метода расчета материалов в интерфейс

import sys
import logging
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSpinBox, QDoubleSpinBox, QComboBox,
    QPushButton, QMessageBox
)
import psycopg2

# Импортируем метод расчёта из задания 2
sys.path.append("../Разработка ядра алгоритма расчета материалов")
from business_logic import calculate_materials, MATERIAL_DEFECT

logging.basicConfig(
    filename="app.log",
    level=logging.ERROR,
    format="%(asctime)s — %(levelname)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

DB_CONFIG = {
    "dbname": "partners_db",
    "user": "mac",
    "host": "localhost",
    "port": 5432
}

def load_product_types():
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT product_type_id, type_name FROM product_types ORDER BY type_name")
                return cur.fetchall()
    except Exception as e:
        logging.error(f"Ошибка загрузки типов продукции: {e}")
        return []


class CalculatorWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CRM: Калькулятор расхода материалов")
        self.setMinimumWidth(400)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Тип продукции
        layout.addWidget(QLabel("Тип продукции:"))
        self.product_type_box = QComboBox()
        types = load_product_types()
        for type_id, type_name in types:
            self.product_type_box.addItem(type_name, type_id)
        layout.addWidget(self.product_type_box)

        # Тип материала
        layout.addWidget(QLabel("Тип материала:"))
        self.material_type_box = QComboBox()
        for mat_id in MATERIAL_DEFECT:
            self.material_type_box.addItem(f"Материал {mat_id}", mat_id)
        layout.addWidget(self.material_type_box)

        # Количество
        layout.addWidget(QLabel("Количество продукции (шт.):"))
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 1000000)
        layout.addWidget(self.quantity_spin)

        # Параметр 1
        layout.addWidget(QLabel("Параметр 1:"))
        self.param1_spin = QDoubleSpinBox()
        self.param1_spin.setRange(0.0, 10000.0)
        self.param1_spin.setDecimals(2)
        layout.addWidget(self.param1_spin)

        # Параметр 2
        layout.addWidget(QLabel("Параметр 2:"))
        self.param2_spin = QDoubleSpinBox()
        self.param2_spin.setRange(0.0, 10000.0)
        self.param2_spin.setDecimals(2)
        layout.addWidget(self.param2_spin)

        # Кнопка расчёта
        btn = QPushButton("Рассчитать")
        btn.clicked.connect(self._on_calculate)
        layout.addWidget(btn)

        # Результат
        self.result_label = QLabel("Результат: —")
        self.result_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.result_label)

    def _on_calculate(self):
        product_type_id = self.product_type_box.currentData()
        material_type_id = self.material_type_box.currentData()
        quantity = self.quantity_spin.value()
        param_1 = self.param1_spin.value()
        param_2 = self.param2_spin.value()

        result = calculate_materials(product_type_id, material_type_id, quantity, param_1, param_2)

        if result == -1:
            QMessageBox.warning(self, "Ошибка", "Некорректные данные. Проверьте параметры.")
            self.result_label.setText("Результат: ошибка")
        else:
            self.result_label.setText(f"Результат: {result} ед. материала")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CalculatorWindow()
    window.show()
    sys.exit(app.exec_())
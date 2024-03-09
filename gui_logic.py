import matplotlib
import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog
from PyQt5 import QtWidgets, QtCore
from gui import Ui_Dialog
from drawing.drawer import Drawer as drawer


matplotlib.use('TkAgg')


class GuiProgram(Ui_Dialog):
    """ Класс контроллер - интерпретирует действия пользователя """

    def __init__(self, dialog: QtWidgets.QDialog) -> None:
        """ Вызывается при создании нового объекта класса """
        Ui_Dialog.__init__(self)
        dialog.setWindowFlags(  # Передаем флаги создания окна
            QtCore.Qt.WindowCloseButtonHint |  # Кнопка закрытия
            QtCore.Qt.WindowMaximizeButtonHint |  # Кнопка развернуть
            QtCore.Qt.WindowMinimizeButtonHint  # Кнопка свернуть
        )
        # Устанавливаем пользовательский интерфейс
        self.setupUi(dialog)

        # ПОЛЯ КЛАССА
        # Параметры 1 графика
        self.drawer_1 = drawer(
            layout=self.layout_plot_1,
            widget=self.widget_plot_1
        )
        # Параметры 2 графика
        self.drawer_2 = drawer(
            layout=self.layout_plot_2,
            widget=self.widget_plot_2
        )

        self.difference_gamma = []
        self.frequency = []
        self.gamma_with_gas = []
        self.gamma_without_gas = []

        # ДЕЙСТВИЯ ПРИ ВКЛЮЧЕНИИ
        self.button_with_gas.clicked.connect(self.push_with_gas)
        self.button_without_gas.clicked.connect(self.push_without_gas)
        self.button_difference.clicked.connect(self.draw_difference_between_file)

    def push_with_gas(self):
        path_file, _ = QFileDialog.getOpenFileName()
        self.frequency, self.gamma_with_gas = self.get_data_from_file(path_file)
        self.draw_gas()

    def push_without_gas(self):
        path_file, _ = QFileDialog.getOpenFileName()
        self.frequency, self.gamma_without_gas = self.get_data_from_file(path_file)
        self.draw_gas()

    # ФУНКЦИЯ ПАРСИНГА ДАННЫХ ИЗ ФАЙЛА
    def get_data_from_file(self, path_file: str):
        frequency_array = []
        gamma_array = []
        file = open(path_file, "r")
        file.readline()
        text = file.readline()
        while "*" not in text:
            array_num = text.split("\t")
            frequency = float(array_num[1])
            gamma = float(array_num[4])
            frequency_array.append(frequency)
            gamma_array.append(gamma)
            text = file.readline()
        file.close()

        return frequency_array, gamma_array

    # ФУНКЦИЯ ОТРИСОВКИ ДВУХ ГРАФИКОВ НА ХОЛСТЕ
    def draw_gas(self):
        # Проверка, что данные не пустые
        if self.gamma_with_gas is None and self.gamma_without_gas is None:
            return

        # Проверка, что оба значения загружены
        if self.gamma_with_gas and self.gamma_without_gas:
            # Рисуем два графика
            self.drawer_1.draw_one_line_xyy(
                self.frequency, self.gamma_with_gas, self.gamma_without_gas
            )

        # Если загружен только газ
        elif self.gamma_with_gas:
            # Рисуем один график
            self.drawer_1.draw_one_line_xy(
                self.frequency, self.gamma_with_gas
            )

        # Если загружен только пустой
        elif self.gamma_without_gas:
            # Рисуем один график
            self.drawer_1.draw_one_line_xy(
                self.frequency, self.gamma_without_gas
            )

    # ФУНКЦИЯ ОТРИСОВКИ РАЗНИЦЫ И ПОРОГОГО ЗНАЧЕНИЯ
    def draw_difference_between_file(self):
        # Считывание процента из текста
        percent = self.line_procent.text()

        # Использования модуля numpy для производительности программы
        gamma_with_gas = np.array(self.gamma_with_gas)
        gamma_without_gas = np.array(self.gamma_without_gas)

        # Вычитание, загрузка и отрисовка графика
        self.difference_gamma = abs(gamma_with_gas - gamma_without_gas)
        if percent != "":
            threshold_value = max(self.difference_gamma) * (float(percent) / 100)
            self.drawer_2.draw_one_line_2xy(
                self.frequency, self.difference_gamma, threshold_value
            )
        else:
            self.drawer_2.draw_one_line_xy(self.frequency, self.difference_gamma)


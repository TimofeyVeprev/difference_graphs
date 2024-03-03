import matplotlib
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

        # ДЕЙСТВИЯ ПРИ ВКЛЮЧЕНИИ
        self.button_with_gas.clicked.connect(self.push_with_gas)
        self.button_without_gas.clicked.connect(self.push_without_gas)

    def push_with_gas(self):
        path_file, _ = QFileDialog.getOpenFileName()
        self.get_data_with_gas(path_file)

    def push_without_gas(self):
        path_file, _ = QFileDialog.getOpenFileName()
        self.get_data_with_gas(path_file)

    # ФУНКЦИЯ ПАРСИНГА ДАННЫХ ИЗ ФАЙЛА
    def get_data_with_gas(self, path_file):
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
        self.drawer_1.draw_one_line_xy(frequency_array, gamma_array)

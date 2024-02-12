import matplotlib
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog

from gui import Ui_Dialog
from drawing.drawer import Drawer as drawer

matplotlib.use('TkAgg')


class GuiProgram(Ui_Dialog):
    """ Класс контроллер - интерпретирует действия пользователя """

    def __init__(self, dialog: QtWidgets.QDialog) -> None:
        """ Вызывается при создании нового объекта класса """
        # Создание окна
        Ui_Dialog.__init__(self)
        # Установка пользовательского интерфейс

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
        self.pushButton.clicked.connect(self.push)

    def push(self):
        array1 = []
        array2 = []
        final_array = []  # список разницы между элементами первого и второго массивов
        path_file, _ = QFileDialog.getOpenFileName()
        file = open(path_file, "r")
        text = file.readlines()
        file.close()
        for i in range(len(text)):
            string = text[i].split()
            array1.append(float(string[0]))
            array2.append(float(string[1]))
        self.drawer_1.draw_two_line(array1, array2)
        final_array = [abs(array1[i] - array2[i]) for i in range(len(array1))]  # списочное выражение, добавление
        # элементов в список
        print(final_array)
        self.drawer_2.draw_one_line(final_array)  # отрисовка разницы

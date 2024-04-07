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

        self.frequency_indexes_above_threshold = []
        self.difference_gamma = []
        self.frequency = []
        self.gamma_with_gas = []
        self.gamma_without_gas = []
        self.threshold_value = 0

        # ДЕЙСТВИЯ ПРИ ВКЛЮЧЕНИИ
        self.button_with_gas.clicked.connect(self.push_with_gas)
        self.button_without_gas.clicked.connect(self.push_without_gas)
        self.button_difference.clicked.connect(self.draw_difference_between_file)
        self.button_the_most_high_gamma.clicked.connect(self.calculation_frequency_indexes_above_threshold)
        self.button_indexes.clicked.connect(self.indexes)

    def push_with_gas(self):
        """ Функция получения директории файла
        с данными с газом и вызова отрисовки графиков """
        path_file, _ = QFileDialog.getOpenFileName()
        self.frequency, self.gamma_with_gas = self.get_data_from_file(path_file)
        self.draw_gas()

    def push_without_gas(self):
        """ Функция получения директории файла
        с данными без газа и вызова отрисовки графиков """
        path_file, _ = QFileDialog.getOpenFileName()
        self.frequency, self.gamma_without_gas = self.get_data_from_file(path_file)
        self.draw_gas()

    def get_data_from_file(self, path_file: str) -> [list[float], list[float]]:
        """ Функция получения, парсинг данных из файла """
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

    def draw_gas(self):
        """ Функция отрисовки двух графиков на холсте """
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

    def draw_difference_between_file(self) -> None:
        """ Функция расчета разницы данных, нахождение порогового значения, отрисовка результата """
        # Считывание процента из текста
        percent = self.line_percent.text()
        # Использования модуля numpy для производительности программы
        gamma_with_gas = np.array(self.gamma_with_gas)
        gamma_without_gas = np.array(self.gamma_without_gas)
        # Вычитание, загрузка и отрисовка графика
        self.difference_gamma = np.array(abs(gamma_with_gas - gamma_without_gas))
        if percent:
            self.threshold_value = max(self.difference_gamma) * (float(percent) / 100)
            self.drawer_2.draw_xy_and_line(
                self.frequency, self.difference_gamma, self.threshold_value
            )
        else:
            self.drawer_2.draw_one_line_xy(self.frequency, self.difference_gamma)

    def calculation_frequency_indexes_above_threshold(self) -> None:
        """ Функция нахождения интервалов индексов частоты, гамма которых выше порога """
        self.frequency_indexes_above_threshold.clear()
        index_interval = []
        last_index = 0
        for i in range(1, np.size(self.difference_gamma)):
            # Если i-тый отсчет оказался больше порога
            if self.difference_gamma[i] >= self.threshold_value:
                # Если индекс идут друг за другом, то записываем их в общий промежуток
                if last_index + 1 == i:
                    index_interval.append(i)
                # Иначе сохраняем интервал в общий список и начинаем новый
                else:
                    if index_interval:
                        self.frequency_indexes_above_threshold.append(index_interval)
                    index_interval = [i]
                # Сохраняем индекс последнего отсчета
                last_index = i
        # Сохраняем результат в класс
        self.frequency_indexes_above_threshold.append(index_interval)
        print(self.frequency_indexes_above_threshold)

        freq_text = ""
        freq = self.search_absorption_line_frequency()
        for i in range(len(freq)):
            freq_text += (str(freq[i]) + " ")
        self.write_line_absorption.setText(freq_text)

    def search_absorption_line_frequency(self) -> list:
        """ Функция определения частот линии поглощения в интервалах """
        medium_freq = []
        freq = []
        # Запускаем основной цикл, проходящий по всему массиву
        for intervals in self.frequency_indexes_above_threshold:
            # Запускаем цикл, проходящий по подмассивам
            for elements in range(len(intervals)):
                print(intervals[elements])
                # Добавляем частоту в промежуточный список по индексу
                medium_freq.append(self.frequency[intervals[elements]])
                print(medium_freq)
            # Находим максимальную частоту в подмассиве и
            # сохраняем ее в массив частот линии поглощения
            freq.append(max(medium_freq))
            # Очищаем промежуточный массив
            medium_freq.clear()
        # Возвращаем итоговый результат
        return freq

    def indexes(self):
        """ Функция отрисовки графиков по заданной частоте """
        # Получение частоты
        freq_index1 = float(self.index_1.text())
        freq_index2 = float(self.index_2.text())

        # Перевод в индексы
        index1 = self.frequency.index(freq_index1)
        index2 = self.frequency.index(freq_index2)

        # Срезы по индексам
        freq_part = self.frequency[index1:index2 + 1]
        gamma_with_gas_part = self.gamma_with_gas[index1:index2 + 1]
        gamma_without_gas_part = self.gamma_without_gas[index1:index2 + 1]

        # Очистка прежних массивов по гамме
        self.gamma_without_gas.clear()
        self.gamma_with_gas.clear()
        self.frequency.clear()

        # Обмен данными
        self.gamma_without_gas = gamma_without_gas_part
        self.gamma_with_gas = gamma_with_gas_part
        self.frequency = freq_part

        # Отрисовка графика
        self.drawer_1.draw_one_line_xyy(
            self.frequency, self.gamma_with_gas, self.gamma_without_gas
        )

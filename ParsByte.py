import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from MainUI import Ui_MainWindow
from datetime import datetime
import ast


class Report(object):
    def __init__(self):
        self.dateRep = datetime.now()
        self.code = [0, 0, 0, 0, 0]
        self.flagsRep = ''
        self.ubatRep = 0.0
        self.adressSensorMaxForce = 0

        self.valueMaxForce = 0.0
        self.temperatureRep = 0.0
        self.humidityRep = 0.0
        self.windDirectRep = 0
        self.cntrap_l = [0, 0, 0, 0, 0]
        self.appAck = [0, 0, 0, 0, 0]
        self.lesAck = [0, 0, 0, 0, 0]

        self.vektor = [0, 0, 0, 0]
        self.forceSense = [0.0, 0.0, 0.0, 0.0, 0.0]
        self.temperatureSense = [0.0, 0.0, 0.0, 0.0, 0.0]

        self.humidityAdd = 0.0
        self.windDirectAdd = 0
        self.windSpeed = 0.0
        self.uzar = 0.0
        self.ubat = 0.0
        self.ucon = 0.0
        self.dqz = 0.0

        self.ID_Number = ''
        self.temperatureHumidity = 0.0
        self.flagStart = 0
        self.countF = 0
        self.currentNumberPack = 0
        self.flag_savedDB = False
        self.flag_errorSavedDB = False


class AppWindow(QMainWindow):
    def __init__(self):
        super(AppWindow, self).__init__()
        self.WindowView = Ui_MainWindow()
        self.WindowView.setupUi(self)
        self.WindowView.btnParse.clicked.connect(self.parseTxtStr)
        self.report = Report()

    def parseTxtStr(self):
        try:
            decoded_bytes = b''
            flag_data = False
            self.WindowView.txtInfo.clear()
            txt_edit = self.WindowView.txtEdit.toPlainText()
            if len(txt_edit) > 0:
                decoded_bytes = ast.literal_eval(txt_edit)
                if len(decoded_bytes) == 72:
                    flag_data = True

            if flag_data:
                self.parsingBytes(decoded_bytes)
            else:
                self.WindowView.txtInfo.append('Неверные данные для преобразования...')

        except Exception as e:
            print('Error: {}'.format(e))

    def parsingBytes(self, b_data):
        try:
            byte_data = b_data
            self.report.dateRep = datetime.now()
            for i in range(5):
                byte_arr = []
                bin_str = ''
                temp_str = ''
                for j in range(11):
                    byte_arr.append(byte_data[i * 11 + j])
                    temp_str = ''.join(bin(byte_arr[j])[2:].zfill(8))
                    bin_str = bin_str + temp_str
                self.parsingBinStr(bin_str, i)

            temp_str = ''
            for j in range(55, 66):
                temp_str = temp_str + chr(byte_data[j])
            self.report.ID_Number = temp_str

            byte_arr = []
            temp_str = ''
            bin_str = ''
            for j in range(66, 72):
                byte_arr.append(byte_data[j])
                temp_str = ''.join(bin(byte_arr[j-66])[2:].zfill(8))
                bin_str = bin_str + temp_str

            self.parsingBinStr(bin_str, 5)

        except Exception as e:
            print('Error: {}'.format(e))

    def parsingBinStr(self, msg, ind):
        try:
            if ind == 0:
                self.WindowView.txtInfo.append('=========== РАПОРТ ОТЧЕТ ===========')
                # код типа рапорта
                temp_bin = msg[:4]
                self.report.code[0] = int('0b' + temp_bin, 2)
                self.WindowView.txtInfo.append('Код типа рапорта: {}'.format(self.report.code[0]))
                self.report.flagsRep = msg[4:16]
                self.WindowView.txtInfo.append('Флаги состояния на момент передачи: {}'.format(self.report.flagsRep))

                # напряжение батареи
                temp_bin = msg[16:24]
                self.report.ubatRep = int('0b' + temp_bin, 2) * 0.1
                self.WindowView.txtInfo.append('Напряжение батареи: {}'.format(self.report.ubatRep))

                # адрес датчика максимального усилия
                temp_bin = msg[28:32]
                self.report.adressSensorMaxForce = int('0b' + temp_bin, 2)
                self.WindowView.txtInfo.append('Адрес датчика максимального усилия: {}'.format(
                                                self.report.adressSensorMaxForce))

                # значение максимального усилия с датчика
                temp_bin = msg[32:56]
                self.report.valueMaxForce = self.BinToDecAdditional(temp_bin, 24) / 10
                self.WindowView.txtInfo.append('Максимальное усилие с датчика: {}'.format(self.report.valueMaxForce))

                # температура окружающей среды
                temp_bin = msg[56:64]
                self.report.temperatureRep = self.BinToDecAdditional(temp_bin, 8) / 2
                self.WindowView.txtInfo.append('Температура окружающей среды: {}'.format(self.report.temperatureRep))

                # значение влажности
                temp_bin = msg[64:72]
                temp_val = int('0b' + temp_bin, 2)
                self.report.humidityRep = round(-4 + 0.648 * temp_val + (-0.00072) * pow(temp_val, 2), 3)
                self.WindowView.txtInfo.append('Значение влажности: {}'.format(self.report.humidityRep))

                # направление ветра
                temp_bin = msg[72:80]
                temp_val = int('0b' + temp_bin, 2)
                self.report.windDirectRep = int(round((360 * temp_val) / 255, 0))
                self.WindowView.txtInfo.append('Направление ветра: {}'.format(self.report.windDirectRep))

                # младшая тетрада счетчика рапортов
                temp_bin = msg[80:84]
                self.report.cntrap_l[0] = int('0b' + temp_bin, 2)
                self.WindowView.txtInfo.append('Младшая тетрада счётчика рапортов: {}'.format(self.report.cntrap_l[0]))

                # служебный флаг для диспетчера
                temp_bin = msg[84:85]
                self.report.appAck[0] = int('0b' + temp_bin, 2)
                self.WindowView.txtInfo.append('Служебный флаг для диспетчера: {}'.format(self.report.appAck[0]))

                # служебный флаг для спутниковой сети
                temp_bin = msg[-1]
                self.report.lesAck[0] = int('0b' + temp_bin, 2)
                self.WindowView.txtInfo.append('Служебный флаг для спутниковой сети: {}'.format(self.report.lesAck[0]))

            if ind == 1:
                self.WindowView.txtInfo.append('\n=== РАПОРТ ДОПОЛНИТЕЛЬНЫЕ ДАННЫЕ 1 ===')
                # код типа рапорта
                temp_bin = msg[:4]
                self.report.code[1] = int('0b' + temp_bin, 2)
                self.WindowView.txtInfo.append('Код типа рапорта: {}'.format(self.report.code[1]))

                # счетчик векторов
                temp_bin = msg[4:8]
                self.report.vektor[0] = int('0b' + temp_bin, 2)
                self.WindowView.txtInfo.append('Счётчик векторов: {}'.format(self.report.vektor[0]))

                # усилие датчика 0
                temp_bin = msg[8:32]
                self.report.forceSense[0] = self.BinToDecAdditional(temp_bin, 24) / 10
                self.WindowView.txtInfo.append('Усилие датчика 0: {}'.format(self.report.forceSense[0]))

                # температура датчика 0
                temp_bin = msg[32:40]
                self.report.temperatureSense[0] = self.BinToDecAdditional(temp_bin, 8) / 2
                self.WindowView.txtInfo.append('Температура датчика 0: {}'.format(self.report.temperatureSense[0]))

                # направление ветра из дополнительных данных1
                temp_bin = msg[40:48]
                temp_val = int('0b' + temp_bin, 2)
                self.report.windDirectAdd = int(round((360 * temp_val) / 255, 0))
                self.WindowView.txtInfo.append('Направление ветра: {}'.format(self.report.windDirectAdd))

                # скорость ветра из дополнительных данных1
                temp_bin = msg[48:64]
                temp_val = int('0b' + temp_bin, 2)
                if temp_val == 0:
                    self.report.windSpeed = 0.0
                else:
                    self.report.windSpeed = round(1000 / temp_val, 3)
                self.WindowView.txtInfo.append('Скорость ветра: {}'.format(self.report.windSpeed))

                # значение влажности
                temp_bin = msg[64:72]
                temp_val = int('0b' + temp_bin, 2)
                self.report.humidityAdd = round(-4 + 0.648 * temp_val + (-0.00072) * pow(temp_val, 2), 3)
                self.WindowView.txtInfo.append('Значение влажности: {}'.format(self.report.humidityAdd))

                # младшая тетрада счетчика рапортов
                temp_bin = msg[80:84]
                self.report.cntrap_l[1] = int('0b' + temp_bin, 2)
                self.WindowView.txtInfo.append('Младшая тетрада счётчика рапортов: {}'.format(self.report.cntrap_l[1]))

                # служебный флаг для диспетчера
                temp_bin = msg[84:85]
                self.report.appAck[1] = int('0b' + temp_bin, 2)
                self.WindowView.txtInfo.append('Служебный флаг для диспетчера: {}'.format(self.report.appAck[1]))

                # служебный флаг для спутниковой сети
                temp_bin = msg[-1]
                self.report.lesAck[1] = int('0b' + temp_bin, 2)
                self.WindowView.txtInfo.append('Служебный флаг для спутниковой сети: {}'.format(self.report.lesAck[1]))

            if ind == 2:
                self.WindowView.txtInfo.append('\n=== РАПОРТ ДОПОЛНИТЕЛЬНЫЕ ДАННЫЕ 2 ===')
                # код типа рапорта
                temp_bin = msg[:4]
                self.report.code[2] = int('0b' + temp_bin, 2)
                self.WindowView.txtInfo.append('Код типа рапорта: {}'.format(self.report.code[2]))

                # счетчик векторов
                temp_bin = msg[4:8]
                self.report.vektor[1] = int('0b' + temp_bin, 2)
                self.WindowView.txtInfo.append('Счётчик векторов: {}'.format(self.report.vektor[1]))

                # усилие датчика 1
                temp_bin = msg[8:32]
                self.report.forceSense[1] = self.BinToDecAdditional(temp_bin, 24) / 10
                self.WindowView.txtInfo.append('Усилие датчика 1: {}'.format(self.report.forceSense[1]))

                # температура датчика 1
                temp_bin = msg[32:40]
                self.report.temperatureSense[1] = self.BinToDecAdditional(temp_bin, 8) / 2
                self.WindowView.txtInfo.append('Температура датчика 1: {}'.format(self.report.temperatureSense[1]))

                # усилие датчика 2
                temp_bin = msg[40:64]
                self.report.forceSense[2] = self.BinToDecAdditional(temp_bin, 24) / 10
                self.WindowView.txtInfo.append('Усилие датчика 2: {}'.format(self.report.forceSense[2]))

                # температура датчика 2
                temp_bin = msg[64:72]
                self.report.temperatureSense[2] = self.BinToDecAdditional(temp_bin, 8) / 2
                self.WindowView.txtInfo.append('Температура датчика 2: {}'.format(self.report.temperatureSense[2]))

                # младшая тетрада счетчика рапортов
                temp_bin = msg[80:84]
                self.report.cntrap_l[2] = int('0b' + temp_bin, 2)
                self.WindowView.txtInfo.append('Младшая тетрада счётчика рапортов: {}'.format(self.report.cntrap_l[2]))

                # служебный флаг для диспетчера
                temp_bin = msg[84:85]
                self.report.appAck[2] = int('0b' + temp_bin, 2)
                self.WindowView.txtInfo.append('Служебный флаг для диспетчера: {}'.format(self.report.appAck[2]))

                # служебный флаг для спутниковой сети
                temp_bin = msg[-1]
                self.report.lesAck[2] = int('0b' + temp_bin, 2)
                self.WindowView.txtInfo.append('Служебный флаг для спутниковой сети: {}'.format(self.report.lesAck[2]))

            if ind == 3:
                self.WindowView.txtInfo.append('\n=== РАПОРТ ДОПОЛНИТЕЛЬНЫЕ ДАННЫЕ 3 ===')
                # код типа рапорта
                temp_bin = msg[:4]
                self.report.code[3] = int('0b' + temp_bin, 2)
                self.WindowView.txtInfo.append('Код типа рапорта: {}'.format(self.report.code[3]))

                # счетчик векторов
                temp_bin = msg[4:8]
                self.report.vektor[2] = int('0b' + temp_bin, 2)
                self.WindowView.txtInfo.append('Счётчик векторов: {}'.format(self.report.vektor[2]))

                # усилие датчика 3
                temp_bin = msg[8:32]
                self.report.forceSense[3] = self.BinToDecAdditional(temp_bin, 24) / 10
                self.WindowView.txtInfo.append('Усилие датчика 3: {}'.format(self.report.forceSense[3]))

                # температура датчика 3
                temp_bin = msg[32:40]
                self.report.temperatureSense[3] = self.BinToDecAdditional(temp_bin, 8) / 2
                self.WindowView.txtInfo.append('Температура датчика 3: {}'.format(self.report.temperatureSense[3]))

                # усилие датчика 4
                temp_bin = msg[40:64]
                self.report.forceSense[4] = self.BinToDecAdditional(temp_bin, 24) / 10
                self.WindowView.txtInfo.append('Усилие датчика 4: {}'.format(self.report.forceSense[4]))

                # температура датчика 4
                temp_bin = msg[64:72]
                self.report.temperatureSense[4] = self.BinToDecAdditional(temp_bin, 8) / 2
                self.WindowView.txtInfo.append('Температура датчика 4: {}'.format(self.report.temperatureSense[4]))

                # младшая тетрада счетчика рапортов
                temp_bin = msg[80:84]
                self.report.cntrap_l[3] = int('0b' + temp_bin, 2)
                self.WindowView.txtInfo.append('Младшая тетрада счётчика рапортов: {}'.format(self.report.cntrap_l[3]))

                # служебный флаг для диспетчера
                temp_bin = msg[84:85]
                self.report.appAck[3] = int('0b' + temp_bin, 2)
                self.WindowView.txtInfo.append('Служебный флаг для диспетчера: {}'.format(self.report.appAck[3]))

                # служебный флаг для спутниковой сети
                temp_bin = msg[-1]
                self.report.lesAck[3] = int('0b' + temp_bin, 2)
                self.WindowView.txtInfo.append('Служебный флаг для спутниковой сети: {}'.format(self.report.lesAck[3]))

            if ind == 4:
                self.WindowView.txtInfo.append('\n=== РАПОРТ ДОПОЛНИТЕЛЬНЫЕ ДАННЫЕ 4 ===')
                # код типа рапорта
                temp_bin = msg[:4]
                self.report.code[4] = int('0b' + temp_bin, 2)
                self.WindowView.txtInfo.append('Код типа рапорта: {}'.format(self.report.code[4]))

                # счетчик векторов
                temp_bin = msg[4:8]
                self.report.vektor[3] = int('0b' + temp_bin, 2)
                self.WindowView.txtInfo.append('Счётчик векторов: {}'.format(self.report.vektor[3]))

                # напряжение зарядки
                temp_bin = msg[8:16]
                self.report.uzar = round(int('0b' + temp_bin, 2) * 0.1, 2)
                self.WindowView.txtInfo.append('Напряжение зарядки: {}'.format(self.report.uzar))

                # напряжение батареи
                temp_bin = msg[16:24]
                self.report.ubat = round(int('0b' + temp_bin, 2) * 0.1, 2)
                self.WindowView.txtInfo.append('Напряжение батареи: {}'.format(self.report.ubat))

                # напряжение контроллера
                temp_bin = msg[24:32]
                self.report.ucon = round(int('0b' + temp_bin, 2) * 0.1, 2)
                self.WindowView.txtInfo.append('Напряжение контроллера: {}'.format(self.report.ucon))

                # разность заряда и разряда батареи
                temp_bin = msg[32:64]
                self.report.dqz = self.BinToDecAdditional(temp_bin, 32) * 0.1
                self.WindowView.txtInfo.append('Разнось заряда и разряда батареи: {}'.format(self.report.dqz))

                # младшая тетрада счетчика рапортов
                temp_bin = msg[80:84]
                self.report.cntrap_l[4] = int('0b' + temp_bin, 2)
                self.WindowView.txtInfo.append('Младшая тетрада счётчика рапортов: {}'.format(self.report.cntrap_l[4]))

                # служебный флаг для диспетчера
                temp_bin = msg[84:85]
                self.report.appAck[4] = int('0b' + temp_bin, 2)
                self.WindowView.txtInfo.append('Служебный флаг для диспетчера: {}'.format(self.report.appAck[4]))

                # служебный флаг для спутниковой сети
                temp_bin = msg[-1]
                self.report.lesAck[4] = int('0b' + temp_bin, 2)
                self.WindowView.txtInfo.append('Служебный флаг для путниковой сети: {}'.format(self.report.lesAck[4]))

            if ind == 5:
                self.WindowView.txtInfo.append('\n=== РАПОРТ ДОПОЛНИТЕЛЬНЫЕ ДАННЫЕ 5 ===')
                # номер телефона
                self.WindowView.txtInfo.append('Номер телефона: {}'.format(self.report.ID_Number))
                # расчет температуры датчика влажности
                temp_str = msg[:16]
                self.report.temperatureHumidity = -39.6 + 0.01 * int('0b' + temp_str, 2)
                self.WindowView.txtInfo.append('Температура датчика влажности: {}'.format(
                                                self.report.temperatureHumidity))

                # флаг причины запуска передачи
                temp_str = msg[16:24]
                self.report.flagStart = int('0b' + temp_str, 2)
                txt_log = 'Причина запуска передачи (код: ' + str(self.report.flagStart) + ') - '
                if self.report.flagStart == 1:
                    txt_log = txt_log + '\n\tЗапуск по окончании интервала в нормальных условиях'
                if self.report.flagStart == 2:
                    txt_log = txt_log + '\n\tПервый запуск при превышении усилия'
                if self.report.flagStart == 3:
                    txt_log = txt_log + '\n\tПовторный запуск при превышении усилия по окончании интервала'

                self.WindowView.txtInfo.append('{}'.format(txt_log))

                # Счетчик передач после окончания превышения усилия
                temp_str = msg[24:32]
                self.report.countF = int('0b' + temp_str, 2)
                self.WindowView.txtInfo.append('Счётчик передач после окончания превышения усилия: {}'.format(
                                                self.report.countF))

                # Текущий номер посыллки
                temp_str = msg[32:40]
                self.report.currentNumberPack = int('0b' + temp_str, 2)
                self.WindowView.txtInfo.append('Текущий номер посылки: {}'.format(self.report.currentNumberPack))

        except Exception as e:
            print('Error: {}'.format(e))

    def DecToBinAdditional(self, value_dec, bits=8):
        if value_dec < 0:
            str_bits = bin(abs(value_dec))
            str_bits = str_bits[2:].zfill(bits)

            val_temp = 2 ** bits - int('0b' + str_bits, 2)
            str_bin = bin(val_temp)
            str_bin = str_bin[2:].zfill(bits)
        else:
            str_bin = bin(value_dec)
            str_bin = str_bin[2:].zfill(bits)

        return str_bin

    def BinToDecAdditional(self, str_bits, bits=8):
        if str_bits[:1] == '1':
            val_temp = 2 ** bits - int('0b' + str_bits, 2)
            val_temp = -val_temp
        else:
            val_temp = int('0b' + str_bits, 2)

        return val_temp

    def BinToDec(self, str_bits):
        rev_str = ''.join(reversed(str_bits))
        val_dec = 0
        for i in range(len(rev_str)):
            val_dec = val_dec + int(rev_str[i]) * (2 ** i)

        return val_dec


def main():
    app = QApplication(sys.argv)
    window=AppWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

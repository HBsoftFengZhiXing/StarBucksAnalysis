# -*- coding: utf-8 -*-
# __Author__: Sdite, amyy4, JX-Soleil, hzgege
# __Email__ : a122691411@gmail.com

import os, time
import platform
import threading
import pandas as pd
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import *
from PyQt5.QtGui import QIcon, QIntValidator, QDoubleValidator
from PyQt5.QtCore import QUrl
from drawThread import DrawThread
from pythonJsInteractObject import PythonJsInteractObject
from draw import  *


class UI(QMainWindow):
    """docstring for UI"""

    # 以下三个常量是用于分别标记查询的类型
    # 以便确定查询的类型来保存相应查询的时间
    FINDTOPKWITHKEYWORD = 1
    FINDTOPKWITHOUTKEYWORD = 2
    FINDRANGE = 3

    def __init__(self):
        super(UI, self).__init__()

        if not os.path.exists('./html'):
            os.mkdir('./html')

        self.t = None
        self.hasOpenFile = False

        # 每种查询时延的列表
        self.topKTimeWithoutKeyWord = []
        self.topKTimeWithKeyWord = []
        self.rangeTime = []

        # 每种查询的k或r值
        self.topKWithoutKeyWord = []
        self.topKWithKeyWord = []
        self.range = []

        self.initUI()

    # 初始化UI
    def initUI(self):
        # 将任务栏图标改成 image/StarBucks.png
        if platform.system() == 'Windows':
            # windows任务栏要这样设置才能和图标一致
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "image/StarBucks.png")

        self.setWindowTitle('星巴克数据分析')
        self.setWindowIcon(QIcon('image/StarBucks.png'))

        self.mainWidget = QWidget()  # 主窗体控件
        self.mainLayout = QGridLayout()  # 主窗体layout

        self.menuBar()  # 菜单栏
        self.statusBar()  # 状态栏
        self.setOpenFileMenu()  # 打开文件菜单
        self.setShowQueryTimeMenu()  # 显示时延菜单选项

        self.setShowButton()  # 设置显示统计图的按钮
        self.setFindInfoWidget()

        self.setWebEngineView()

        self.mainWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainWidget)

        self.center()  # 居中窗口， 但固定窗口大小后失效

        self.show()

    # 设置webEngineView
    def setWebEngineView(self):
        self.webEngine = QWebEngineView(self)

        # 设置JS和Python的交互通道
        self.pWebChannel = QWebChannel(self.webEngine.page())
        self.pythonJsInteractObj = PythonJsInteractObject(self)
        self.pWebChannel.registerObject('interactObj', self.pythonJsInteractObj)
        self.webEngine.page().setWebChannel(self.pWebChannel)
        self.pythonJsInteractObj.sigReceivedMessFromJS.connect(self.onReceiveMessageFromJS)

        self.mainLayout.addWidget(self.webEngine, 1, 8, 11, 15)

    # 从JS获取数据
    def onReceiveMessageFromJS(self, strParameter):
        print('ReceiveFromJS', strParameter)
        data = strParameter.split(' ')  # Js传过来的数据格式为 '行号 分数'

        self.csv_file['Score'].iloc[int(data[0])] += data[1] + ' '  # 添加分数到记录中

        score = self.csv_file['Score'].iloc[int(data[0])].strip().split(' ')
        avgScore = sum([float(s) for s in score]) / len(score)  # 求平均分
        self.csv_file['AvgScore'].iloc[int(data[0])] = avgScore
        # print('Score:', score)
        # print('AvgScore:', avgScore)

    # 加载html
    def showInWebEngineView(self, button, fileName, type=None):
        button.setEnabled(True)
        self.statusBar().showMessage(self.t.time)
        t = float(self.t.time.split(' ')[1][:-1])  # 去掉中文字符和单位s
        if type == self.FINDRANGE:
            self.rangeTime.append(t)
        elif type == self.FINDTOPKWITHKEYWORD:
            self.topKTimeWithKeyWord.append(t)
        elif type == self.FINDTOPKWITHOUTKEYWORD:
            self.topKTimeWithoutKeyWord.append(t)
        self.loadUrl(fileName)

    # 加载html
    def loadUrl(self, fileName):
        self.webEngine.page().load(QUrl.fromLocalFile(fileName))

    # 检查输入是否合法
    def checkLongAndLat(self):
        self.longitude = self.longitudeEdit.text()
        self.latitude = self.latitudeEdit.text()
        if self.longitude == "":
            QMessageBox.warning(self, "警告", "请输入经度", QMessageBox.Ok)
            return False

        try:
            self.longitude = float(self.longitude)
            if self.longitude > 180 or self.longitude < -180:
                QMessageBox.warning(self, "错误", "经度在-180~180之间", QMessageBox.Ok)
                return False
        except:
            QMessageBox.warning(self, "错误", "请输入数字", QMessageBox.Ok)
            return False

        if self.latitude == "":
            QMessageBox.warning(self, "警告", "请输入纬度", QMessageBox.Ok)
            return False

        try:
            self.latitude = float(self.latitude)
            if self.latitude > 90 or self.latitude < -90:
                QMessageBox.warning(self, "错误", "纬度在-90~90之间", QMessageBox.Ok)
                return False
        except:
            QMessageBox.warning(self, "错误", "请输入数字", QMessageBox.Ok)
            return False
        return True

    # top-k的输入框，按钮的控件
    def setFindInfoWidget(self):
        longitudeLabel = QLabel()
        latitudeLabel = QLabel()
        rangeLabel = QLabel()
        kLabel = QLabel()
        keyWordLabel = QLabel()

        longitudeLabel.setText("经度: ")
        latitudeLabel.setText("纬度: ")
        rangeLabel.setText("range:")
        kLabel.setText("k: ")
        keyWordLabel.setText("关键词：")

        self.longitudeEdit = QLineEdit()
        self.latitudeEdit = QLineEdit()
        self.rangeEdit = QLineEdit()
        self.kEdit = QLineEdit()
        self.keyWordEdit = QLineEdit()

        longitudeValidator = QDoubleValidator(self)
        longitudeValidator.setRange(-180.00, 180.00)
        longitudeValidator.setNotation(QDoubleValidator.StandardNotation)
        longitudeValidator.setDecimals(2)
        self.longitudeEdit.setValidator(longitudeValidator)

        latitudeValidator = QDoubleValidator(self)
        latitudeValidator.setRange(-90.00, 90.00)
        latitudeValidator.setNotation(QDoubleValidator.StandardNotation)
        latitudeValidator.setDecimals(2)
        self.latitudeEdit.setValidator(latitudeValidator)

        kIntValidator = QIntValidator(self)
        kIntValidator.setRange(0, 25000)
        self.rangeEdit.setPlaceholderText("单位: km")
        self.rangeEdit.setValidator(kIntValidator)

        self.findRangeButton = QPushButton()
        self.findRangeButton.setText("查找range")
        self.findRangeButton.setEnabled(False)
        self.findRangeButton.clicked.connect(lambda : self.findRange(self.findRangeButton))

        self.findTopKButton = QPushButton()
        self.findTopKButton.setText("查找top-k")
        self.findTopKButton.setEnabled(False)
        self.findTopKButton.clicked.connect(lambda : self.findTopK(self.findTopKButton))

        self.longitudeEdit.setStatusTip("经度取值范围: -180.00-180.00")
        self.latitudeEdit.setStatusTip("纬度取值范围: -180.00-180.00")
        self.rangeEdit.setStatusTip("半径取值: 0-25000")

        vBox = QVBoxLayout(self)
        vBox.addWidget(longitudeLabel)
        vBox.addWidget(self.longitudeEdit, 0)
        vBox.addWidget(latitudeLabel)
        vBox.addWidget(self.latitudeEdit, 0)
        vBox.addWidget(rangeLabel)
        vBox.addWidget(self.rangeEdit, 0)
        vBox.addWidget(kLabel)
        vBox.addWidget(self.kEdit, 0)
        vBox.addWidget(keyWordLabel)
        vBox.addWidget(self.keyWordEdit, 0)
        vBox.addWidget(self.findRangeButton, 0)
        vBox.addWidget(self.findTopKButton, 0)

        self.longitudeEdit.setEnabled(False)
        self.latitudeEdit.setEnabled(False)
        self.rangeEdit.setEnabled(False)
        self.kEdit.setEnabled(False)
        self.keyWordEdit.setEnabled(False)

        hWidget = QWidget()
        hWidget.setLayout(vBox)
        self.mainLayout.addWidget(hWidget, 2, 3, 6, 4)

    # range范围查询
    def findRange(self, button):
        if not self.checkLongAndLat():
            return

        r = self.rangeEdit.text()

        if r == "":
            QMessageBox.warning(self, "警告", "请输入range值", QMessageBox.Ok)
            return

        button.setEnabled(False)

        r = int(r)

        self.kEdit.clear()
        self.keyWordEdit.clear()

        self.loadUrl('/config/loadingHtml/loading.html')
        self.t = DrawThread(
            target=drawRangeMap,
            args=(self.csv_file,
                  self.longitude,
                  self.latitude,
                  r,
                  'html/rangeMap.html', '距离range图'))
        type = self.FINDRANGE
        self.range.append(r)
        self.t.endTrigger.connect(
            lambda: self.showInWebEngineView(button, '/html/rangeMap.html', type))
        self.t.start()

    # topK查询
    def findTopK(self, button):
        if not self.checkLongAndLat():
            return


        k = self.kEdit.text()
        keyword = self.keyWordEdit.text()

        if k == "":
            QMessageBox.warning(self, "警告", "请输入k值", QMessageBox.Ok)
            return

        button.setEnabled(False)

        k = int(k)

        self.rangeEdit.clear()

        self.loadUrl('/config/loadingHtml/loading.html')
        self.t = DrawThread(
            target=drawTopKMap,
            args=(
                self.csv_file,
                self.longitude,
                self.latitude,
                k,
                keyword,
                self.data,
                'html/topKMap.html', 'topK点图'))

        if keyword != "":
            type = self.FINDTOPKWITHKEYWORD
            self.topKWithKeyWord.append(k)
        else:
            type = self.FINDTOPKWITHOUTKEYWORD
            self.topKWithoutKeyWord.append(k)

        self.t.endTrigger.connect(lambda: self.showInWebEngineView(button, '/html/topKMap.html', type))
        self.t.start()

    # 扩展显示
    def showExtension(self):
        self.extensionWidget.setVisible(not self.extensionWidget.isVisible())
        if self.extensionWidget.isVisible():
            self.extensionButton.setText("<<")
        else:
            self.extensionButton.setText(">>")

    # 设置基本按钮， 后续可能要重写
    def setShowButton(self):
        self.drawMapButton = QPushButton('世界分布图', self)
        self.drawColorMapButton = QPushButton('国家分布彩色图', self)
        self.countStoreByTimezoneButton_bar = QPushButton('时区店铺数量柱状图', self)
        self.countStoreByTimezoneButton_pie = QPushButton('时区店铺数量饼图', self)
        self.countStoreByCountryButton_bar = QPushButton('国家店铺数量柱状图', self)
        self.countStoreByCountryButton_pie = QPushButton('国家店铺数量饼图', self)

        self.drawMapButton.setEnabled(False)
        self.drawColorMapButton.setEnabled(False)
        self.countStoreByTimezoneButton_bar.setEnabled(False)
        self.countStoreByTimezoneButton_pie.setEnabled(False)
        self.countStoreByCountryButton_bar.setEnabled(False)
        self.countStoreByCountryButton_pie.setEnabled(False)

        self.drawMapButton.clicked.connect(lambda : self.drawMap(self.drawMapButton))
        self.drawColorMapButton.clicked.connect(lambda : self.drawColorMap(self.drawColorMapButton))
        self.countStoreByTimezoneButton_bar.clicked.connect(
            lambda: self.drawBar(self.countStoreByTimezoneButton_bar,
                                 self.csv_file['Timezone'],
                                 'html/timezoneBar.html', '时区店铺数量柱状图'))
        self.countStoreByTimezoneButton_pie.clicked.connect(
            lambda: self.drawPie(
                self.countStoreByTimezoneButton_pie,
                self.csv_file['Timezone'],
                                 'html/timezonePie.html', '时区店铺数量饼图')
        )

        self.countStoreByCountryButton_bar.clicked.connect(
            lambda: self.drawBar(
                self.countStoreByCountryButton_bar,
                self.csv_file['Country'],
                                 'html/countryBar.html', '国家店铺数量柱状图'))
        self.countStoreByCountryButton_pie.clicked.connect(
            lambda: self.drawPie(
                self.countStoreByCountryButton_pie,
                self.csv_file['Country'],
                                 'html/countryPie.html', '国家店铺数量饼图'))

        # 将旧的需求加入到扩展控件中
        self.extensionWidget = QWidget()
        vBox = QVBoxLayout(self)
        vBox.addWidget(self.drawMapButton)
        vBox.addWidget(self.drawColorMapButton)
        vBox.addWidget(self.countStoreByTimezoneButton_bar)
        vBox.addWidget(self.countStoreByTimezoneButton_pie)
        vBox.addWidget(self.countStoreByCountryButton_bar)
        vBox.addWidget(self.countStoreByCountryButton_pie)
        self.extensionWidget.setLayout(vBox)
        self.extensionWidget.hide()

        # 控制显示和隐藏
        self.extensionButton = QPushButton(">>", self)
        self.extensionButton.setCheckable(True)
        self.extensionButton.setAutoDefault(False)
        self.extensionButton.toggled.connect(self.showExtension)

        self.mainLayout.addWidget(self.extensionButton, 1, 3, 1, 1)
        self.mainLayout.addWidget(self.extensionWidget, 1, 1, 7, 1)

    # 画时区店铺数量渐变彩色点
    def drawMap(self, button):
        button.setEnabled(False)
        self.loadUrl('/config/loadingHtml/loading.html')

        self.t = DrawThread(
            target=drawMap,
            args=(self.csv_file, 'html/map.html', '不同时区店铺数量渐变图')
        )
        self.t.endTrigger.connect(lambda: self.showInWebEngineView(button, '/html/map.html'))
        self.t.start()

    # 画国家分布彩色渐变图
    def drawColorMap(self, button):
        button.setEnabled(False)
        self.loadUrl('/config/loadingHtml/loading.html')
        self.t = DrawThread(
            target=drawColorMaps,
            args=(self.csv_file['Country'],
                  'html/colorMap.html', '国家分布彩色图'))
        self.t.endTrigger.connect(lambda: self.showInWebEngineView(button, '/html/colorMap.html'))
        self.t.start()

    # 画柱状图
    def drawBar(self, button, data, fileName='html/bar.html', title=''):
        button.setEnabled(False)
        self.loadUrl('/config/loadingHtml/loading.html')
        self.t = DrawThread(target=drawBar, args=(data, fileName, title))
        self.t.endTrigger.connect(lambda: self.showInWebEngineView(button, '/' + fileName))
        self.t.start()

    # 画饼图
    def drawPie(self, button, data, fileName='html/pie.hmtl', title=''):
        button.setEnabled(False)
        self.loadUrl('/config/loadingHtml/loading.html')
        self.t = DrawThread(target=drawPie, args=(data, fileName, title))
        self.t.endTrigger.connect(lambda: self.showInWebEngineView(button, '/' + fileName))
        self.t.start()

    # 显示时延
    def showTime(self, button):
        data = [
            (self.rangeTime, self.range, 'range查找'),
            (self.topKTimeWithoutKeyWord, self.topKWithoutKeyWord, 'topK无关键字'),
            (self.topKTimeWithKeyWord, self.topKWithKeyWord, 'topK有关键字')
        ]
        self.t = DrawThread(target=drawLineChart, args=(data, 'html/showTime.html'))
        self.t.endTrigger.connect(lambda: self.showInWebEngineView(button, '/html/showTime.html'))
        self.t.start()

    # 设置显示时延的菜单
    def setShowQueryTimeMenu(self):
        menuBar = self.menuBar()
        viewMenu = menuBar.addMenu('View')

        showQueryTimeMenu = QAction(QIcon('image/time.png'), 'show time', self)
        showQueryTimeMenu.setShortcut('Ctrl+1')
        showQueryTimeMenu.setStatusTip('显示时延')
        showQueryTimeMenu.triggered.connect(lambda : self.showTime(showQueryTimeMenu))

        viewMenu.addAction(showQueryTimeMenu)

    # 设置打开文件的功能
    def setOpenFileMenu(self):
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('File')

        openFile = QAction(QIcon('image/open.png'), 'open file', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('打开文件')
        openFile.triggered.connect(self.showFileDialog)

        fileMenu.addAction(openFile)

    # 显示文件对话框
    def showFileDialog(self):
        # 打开文件，只允许打开'csv'文件
        filePath = QFileDialog.getOpenFileName(self, caption='打开文件', directory='./',
                                               filter='*.csv')
        if filePath[0]:
            file = filePath[0]
            filename = os.path.split(file)[1].split('.')[0]

            savePickle = 'config/' + filename + '.pickle'
            threading.Thread(target=self.openFile, args=(file, savePickle)).start()
            self.setWindowTitle(file)

    # 检查上次打开的这个csv文件修改时间和这次打开的这个csv文件的时间是否一致
    def checkFile(self, file, savePickle):
        savePickleChange = savePickle + 'change'
        with open(savePickleChange, 'rb') as f:
            changeTime = pickle.load(f)
        nowChangeTime = time.localtime(os.stat(file).st_mtime)

        # 如果时间一致，表明两个文件相同， 不一致则需要重新打开
        if changeTime == nowChangeTime:
            return True
        else:
            return False

    # 打开文件
    def openFile(self, file, savePickle):
        self.file = file
        self.savePickle = savePickle
        if os.path.isfile(savePickle) and self.checkFile(file, savePickle):
            # 该文件曾被打开过， 有pickle缓存
            # 该文件没有被修改过
            with open(savePickle, 'rb') as f:
                self.csv_file = pickle.load(f)

            with open(savePickle + 'data', 'rb') as f:
                self.data = pickle.load(f)
        else:
            # 该文件没有被打开过
            # 一是打开它
            # 二是保存该文件的csv类型， 提高下次打开效率
            # 三是保存该文件的最后修改时间，用于下次打开时判断是否被修改过
            self.csv_file = pd.read_csv(file)

            with open(savePickle, 'wb') as f:
                pickle.dump(self.csv_file, f)

            try:
                self.csv_file['AvgScore']
            except:
                self.csv_file['AvgScore'] = 0

            try:
                self.csv_file['Score']
            except:
                self.csv_file['Score'] = ''

            try:
                self.csv_file['Id']
            except:
                self.csv_file['Id'] = list(range(len(self.csv_file)))


            # self.data是每行整合成一行的列表
            csv_file_tmp = self.csv_file.fillna("").astype(str)
            self.data = [" ".join(list(csv_file_tmp.iloc[x])) for x in
                         range(len(csv_file_tmp))]

            with open(savePickle + 'data', 'wb') as f:
                pickle.dump(self.data, f)

            changeTime = time.localtime(os.stat(file).st_mtime)
            savePickleChange = savePickle + 'change'
            with open(savePickleChange, 'wb') as f:
                pickle.dump(changeTime, f)

        self.drawMapButton.setEnabled(True)
        self.drawColorMapButton.setEnabled(True)
        self.countStoreByTimezoneButton_bar.setEnabled(True)
        self.countStoreByTimezoneButton_pie.setEnabled(True)
        self.countStoreByCountryButton_bar.setEnabled(True)
        self.countStoreByCountryButton_pie.setEnabled(True)
        self.findTopKButton.setEnabled(True)
        self.findRangeButton.setEnabled(True)

        self.longitudeEdit.setEnabled(True)
        self.latitudeEdit.setEnabled(True)
        self.kEdit.setEnabled(True)
        self.rangeEdit.setEnabled(True)
        self.keyWordEdit.setEnabled(True)

        kIntValidator = QIntValidator(self)
        kIntValidator.setRange(0, len(self.csv_file))
        self.kEdit.setPlaceholderText("0-" + str(len(self.csv_file)))
        self.kEdit.setStatusTip("k值范围: 0-" + str(len(self.csv_file)))
        self.kEdit.setValidator(kIntValidator)

        self.hasOpenFile = True

    # 窗口居中
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, *args, **kwargs):
        super().closeEvent(*args, **kwargs)

        if self.hasOpenFile:

            try:
                self.csv_file = self.csv_file.drop(['TimeZoneCount'], axis=1)
            except:
                pass

            try:
                self.csv_file = self.csv_file.drop(['info'], axis=1)
            except:
                pass

            try:
                self.csv_file = self.csv_file.drop(['Distance'], axis=1)
            except:
                pass

            self.csv_file.to_csv('directory.csv')       # 保存csv_file

            with open(self.savePickle, 'wb') as f:
                pickle.dump(self.csv_file, f)

            # self.data是每行整合成一行的列表
            # csv_file_tmp = self.csv_file.fillna("").astype(str)
            # self.data = [" ".join(list(csv_file_tmp.iloc[x])) for x in
            #              range(len(csv_file_tmp))]
            #
            # with open(self.savePickle + 'data', 'wb') as f:
            #     pickle.dump(self.data, f)

            changeTime = time.localtime(os.stat(self.file).st_mtime)
            savePickleChange = self.savePickle + 'change'
            with open(savePickleChange, 'wb') as f:
                pickle.dump(changeTime, f)

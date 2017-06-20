#!/usr/bin/env python
# encoding=utf-8
import sys
import os
import ConfigParser
import codecs
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox, QGridLayout
from PyQt5.QtWidgets import QLineEdit, QLabel, QTextEdit, QPushButton, QFileDialog
from PyQt5 import QtCore, QtGui
from ParseHtml import ParseHtml


class EmittingStream(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))


class PicTool(QWidget):

    def __init__(self):

        # 解决中文编码问题
        reload(sys)
        sys.setdefaultencoding('utf-8')

        super(PicTool, self).__init__()

        self.url_edit = QLineEdit()
        self.status_edit = QTextEdit()
        self.file_path_label = QLabel('')

        self.read_file_path()

        self.parse_html = ParseHtml(self.url_edit.text(), self.file_path_label.text())

        # 重定向输出
        sys.stdout = EmittingStream(textWritten=self.output_written)
        sys.stderr = EmittingStream(textWritten=self.output_written)

        self.init_ui()

    def __del__(self):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    def output_written(self, text):
        cursor = self.status_edit.textCursor()
        cursor.movePosition(QtGui.QTextCursor.Up)
        cursor.insertText(text)
        self.status_edit.setTextCursor(cursor)
        self.status_edit.ensureCursorVisible()

    def init_ui(self):

        # url地址
        url_label = QLabel('URL地址')
        btn_spider = QPushButton('开始抓取')
        btn_spider.clicked.connect(self.btn_spider)

        # 存储路径
        file_label = QLabel('存储路径')
        btn_open_file = QPushButton('设置路径')
        btn_open_file.clicked.connect(self.btn_set_path)

        # 抓取信息展示
        status_label = QLabel('详细日志')
        self.status_edit.setText('***************准备就绪！*****************')
        self.status_edit.setReadOnly(True)

        # 布局
        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(url_label, 1, 0)
        grid.addWidget(self.url_edit, 1, 1)
        grid.addWidget(btn_spider, 1, 2)

        grid.addWidget(file_label, 2, 0)
        grid.addWidget(self.file_path_label, 2, 1)
        grid.addWidget(btn_open_file, 2, 2)

        grid.addWidget(status_label, 3, 0)
        grid.addWidget(self.status_edit, 3, 1, 5, 1)

        self.setLayout(grid)

        # 定义窗体大小／标题
        self.resize(600, 400)
        self.setWindowTitle(u'抓图工具')

        self.show()

    # 设置文件存储路径
    def btn_set_path(self):
        # 起始路径
        directory = QFileDialog.getExistingDirectory(self, "选取文件夹", os.getcwd())
        if directory != '':
            self.file_path_label.setText(directory)
            cp = ConfigParser.SafeConfigParser()
            cp.read(os.getcwd() + '/config.conf')
            cp.set('base', 'file_path', directory)
            cp.write(open("config.conf", "w"))

        # 抓取按钮执行
    def btn_spider(self):

        if self.url_edit.text() != "":
            self.status_edit.setText('***************准备就绪！*****************')
            # 新建对象，传入参数
            self.parse_html = ParseHtml(self.url_edit.text(), self.file_path_label.text())
            self.parse_html.start()

        else:
            QMessageBox.warning(self, "警告", "请输入URL地址", QMessageBox.Ok)

    # 读取配置文件
    def read_file_path(self):

        if not os.path.exists(os.getcwd() + '/config.conf'):
            with codecs.open(os.getcwd() + '/config.conf', 'wb', 'utf-8') as fp:
                fp.write('[base]\nfile_path = ' + os.getcwd())

        cp = ConfigParser.SafeConfigParser()
        cp.read(os.getcwd() + '/config.conf')
        file_path = str(cp.get('base', 'file_path'))
        self.file_path_label.setText(file_path)

        return file_path

    # 关闭窗口提示

    def closeEvent(self, event):

        msg = QMessageBox.question(self, '提示', '您确定退出', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if msg == QMessageBox.Yes:
            event.accept()

        else:
            event.ignore()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = PicTool()
    sys.exit(app.exec_())

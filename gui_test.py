#! C:\Python36\
# -*- encoding: utf-8 -*-
from soas_network_utils import readin_results_of_community_detection
from soas_rhyme_net_structs import stanza_processor
import os
import sys
from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5 import QtCore, QtGui, QtSvg, QtWidgets
#This is a requirement of Qt: Every GUI app must have exactly one instance of QApplication.
#app = QApplication([])
#label = QLabel('Hello World!')
#label.show()
#app.exec_()
#QtGui.QWindow
if 0:
    class Ui_main_window_form(QtGui.QWindow):#object):
        def setupUi(self, main_window_form):
            print(u'Ui_main_window_form::setupUi()')
            self.main_window_form = main_window_form
            self.main_window_form.setObjectName("main_window_form")
            self.main_window_form.setTitle("Expert Entry Expeditor")
            self.main_win_width = 1120 + 400
            self.main_win_height = 820
            self.main_window_form.resize(self.main_win_width, self.main_win_height) # width, height

            self.textEdit = QtWidgets.QTextEdit()
            #self.btnPress1 = QtWidgets.QPushButton("Button 1")
            #self.btnPress2 = QtWidgets.QPushButton("Button 2")
            layout = QtWidgets.QVBoxLayout()
            layout.addWidget(self.textEdit)
            #layout.addWidget(self.btnPress1)
            #layout.addWidget(self.btnPress2)

            #self.btnPress1.clicked.connect(self.btnPress1_Clicked)
            #self.btnPress2.clicked.connect(self.btnPress2_Clicked)
            self.setLayout(layout)

        def retranslateUi(self, main_window_form):
            main_window_form.setWindowTitle(QtGui.QGuiApplication.translate("main_window_form",
                                                                            "Expert Entry Expeditor",
                                                                            None,
                                                                            QtGui.QGuiApplication.UnicodeUTF8))

        def btnPress1_Clicked(self):
                self.textEdit.setPlainText("Hello PyQt5!\nfrom pythonpyqt.com")

        def btnPress2_Clicked(self):
                self.textEdit.setHtml("<font color='red' size='6'><red>Hello PyQt5!\nHello</font>")

from PyQt5.QtWidgets import QApplication, QWidget,QTextEdit,QVBoxLayout, QHBoxLayout, QPushButton, QLabel
import PyQt5.QtWidgets as QtWidgets
from PyQt5.QtGui import QIcon, QFont
import sys

# based on: https://pythonpyqt.com/pyqt-qtextedit/
class TextEditDemo(QWidget):
        def __init__(self,parent=None):
                super().__init__(parent)

                self.setWindowTitle("Comparing Annotators")
                #self.resize(300,270)
                self.resize(1120 + 400, 820)
                self.top_horz_layout = QHBoxLayout()
                self.top_right_vert_layout = QVBoxLayout()
                self.top_left_vert_layout = QVBoxLayout()
                layout = QVBoxLayout() # main layout
                #
                # Create QButtonGroup for choosing data type
                if 0:
                    self.data_type_rb_group = QtWidgets.QButtonGroup(self.top_left_vert_layout)  # Letter group
                    self.received_shi_RB = QtWidgets.QRadioButton('Received Shi (Lu 1983)')
                    self.data_type_rb_group.addButton(self.received_shi_RB)
                    self.mirrors_RB = QtWidgets.QRadioButton('Mirrors (Kyomeishusei 2015)')
                    self.data_type_rb_group.addButton(self.mirrors_RB)
                    self.stelae_RB = QtWidgets.QRadioButton('Stelae (Mao 2007)')
                    self.data_type_rb_group.addButton(self.stelae_RB)
                    self.top_left_vert_layout.addWidget(self.received_shi_RB)
                    self.top_left_vert_layout.addWidget(self.mirrors_RB)
                    self.top_left_vert_layout.addWidget(self.stelae_RB)
                #
                # Create Radiogroup for choosing Community Detection type
                self.com_det_annotator_type_GB = QtWidgets.QGroupBox('Community Detection Type:')
                self.com_det_annotator_type_GB.setFont(QFont("Sanserif", 12))
                self.singular_RB = QtWidgets.QRadioButton('Singular')
                self.singular_RB.setChecked(True)
                self.singular_RB.toggled.connect(self.on_selected)
                self.top_right_vert_layout.addWidget(self.singular_RB)

                self.combo_RB = QtWidgets.QRadioButton('Combo')
                #self.com_det_annotator_type_rb_group.addButton(self.combo_RB)
                #self.com_det_annotator_type_rb_group.addButton(self.singular_RB)

                #self.singular_RB.toggled
                self.combo_RB.toggled.connect(self.on_selected)
                self.top_right_vert_layout.addWidget(self.combo_RB)
                self.com_det_annotator_type_GB.setLayout(layout)#self.top_right_vert_layout)
                #
                # Add the radiogroups to the top horizontal layout
                #self.top_horz_layout.addLayout(self.top_left_vert_layout)
                self.top_horz_layout.addLayout(self.top_right_vert_layout)

                self.naive_L = QLabel()
                self.naive_L.setText('Naive Annotator')
                self.naive_TE = QTextEdit()
                self.com_det_L = QLabel()
                self.com_det_L.setText('Community Detection Annotator')
                self.com_det_TE = QTextEdit()
                self.schuessler_L = QLabel()
                self.schuessler_L.setText('Schuessler Annotator')
                self.schuessler_TE = QTextEdit()

                self.btnPress1 = QPushButton("Button 1")
                self.btnPress2 = QPushButton("Button 2")


                layout.addLayout(self.top_horz_layout)
                #layout.addWidget(self.com_det_annotator_type_GB)
                #layout.addLayout(self.top)
                layout.addWidget(self.naive_L)
                layout.addWidget(self.naive_TE)
                layout.addWidget(self.com_det_L)
                layout.addWidget(self.com_det_TE)
                layout.addWidget(self.schuessler_L)
                layout.addWidget(self.schuessler_TE)
                layout.addWidget(self.btnPress1)
                layout.addWidget(self.btnPress2)
                self.setLayout(layout)

                self.btnPress1.clicked.connect(self.btnPress1_Clicked)
                self.btnPress2.clicked.connect(self.btnPress2_Clicked)

#        def setup_data_type_RB_group(self):
        def btnPress1_Clicked(self):
                self.textEdit.setPlainText("Hello PyQt5!\nfrom pythonpyqt.com")

        def btnPress2_Clicked(self):
                self.textEdit.setHtml("<font color='red' size='6'><red>Hello PyQt5!\nHello</font>")
        def on_selected(self):
            radio_button = self.sender()
            if radio_button.isChecked():
                print("You have selected : " + radio_button.text())
                #self.label.setText("You have selected : " + radio_button.text())
if __name__ == '__main__':
        app = QApplication(sys.argv)
        win = TextEditDemo()
        win.show()
        sys.exit(app.exec_())

if 0:
    if __name__ == "__main__":
        app = QtGui.QGuiApplication(sys.argv)
        MainWindow = QtGui.QWindow()
        ui = Ui_main_window_form()
        ui.setupUi(MainWindow)
        MainWindow.show()
        sys.exit(app.exec_())

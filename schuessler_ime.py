#! C:\Python36\
# -*- encoding: utf-8 -*-
#import PyQt5.Key_Escape as Key_Escape
from PyQt5 import QtWidgets, uic
#from PyQt5 import QtGui.QColor
from PyQt5.QtGui import QColor, QKeySequence
import PyQt5.QtGui as QtGui
from PyQt5.Qt import QApplication, QClipboard
#import PyQt5.QtCore as Qtcore
import PyQt5.QtCore as QtCore
from soas_network_utils import get_hanproj_dir
from soas_network_utils import readlines_of_utf8_file
from soas_rnetwork_test import delete_file_if_it_exists
from soas_network_utils import append_line_to_output_file
from soas_imported_from_py3 import append_line_to_utf8_file
from soas_network_utils import is_hanzi
from soas_network_utils import exception_chars
from soas_network_utils import if_file_exists
from soas_network_utils import readin_most_complete_schuessler_data
import os
import sys
import subprocess
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QLineEdit, QShortcut
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import QSize
PIPE = -1
STDOUT = -2

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        #QMainWindow.__init__(self, parent=parent)

        self.setMinimumSize(QSize(320, 140))
        self.setWindowTitle("Schuesler LHan IME")

        self.nameLabel = QLabel(self)
        #self.nameLabel.setText('Name:')
        self.line = QLineEdit(self)

        self.line.move(40, 20)
        self.line.resize(240, 32)
        self.nameLabel.move(20, 20)

        self.line.installEventFilter(self)
        self.line.setFont(QtGui.QFont("Times New Roman", 14))

        #self.line.textEdited.connect(self.showCurrentText)
        self.line.textChanged.connect(self.put_text_on_clipboard)
        #self.line.keyPressEvent.connect(self.key_press_event)
        #self.line.key
        #self.shortcut_open = QShortcut(QKeySequence('Ctrl+o'), self)
        #self.shortcut_open.activated.connect(self.on_open)
        if 0:
            self.ctrl_h_event = QShortcut(QKeySequence('Ctrl+h'), self)
            self.ctrl_h_event.activated.connect(self.handle_ctrl_h_event)
            self.ctrl_b_event = QShortcut(QKeySequence('Ctrl+b'), self)
            self.ctrl_b_event.activated.connect(self.handle_ctrl_b_event)
            self.ctrl_c_event = QShortcut(QKeySequence('Ctrl+c'), self)
            self.ctrl_c_event.activated.connect(self.handle_ctrl_c_event)
#-
        self.alt_h_event = QShortcut(QKeySequence('Alt+h'), self)
        self.alt_h_event.activated.connect(self.handle_alt_h_event)
        self.alt_b_event = QShortcut(QKeySequence('Alt+b'), self)
        self.alt_b_event.activated.connect(self.handle_alt_b_event)
        self.alt_c_event = QShortcut(QKeySequence('Alt+c'), self)
        self.alt_c_event.activated.connect(self.handle_alt_c_event)

        self.ctrl_f_event = QShortcut(QKeySequence('Ctrl+f'), self)
        self.ctrl_f_event.activated.connect(self.handle_ctrl_f_event)
        self.ctrl_comma_event = QShortcut(QKeySequence('Ctrl+,'), self)
        self.ctrl_comma_event.activated.connect(self.handle_ctrl_comma_event)
        self.ctrl_qmark_event = QShortcut(QKeySequence('Ctrl+Shift+/'), self)
        self.ctrl_qmark_event.activated.connect(self.handle_ctrl_qmark_event)
        self.ctrl_o_event = QShortcut(QKeySequence('Ctrl+o'), self)
        self.ctrl_o_event.activated.connect(self.handle_ctrl_o_event)
        self.ctrl_e_event = QShortcut(QKeySequence('Ctrl+e'), self)
        self.ctrl_e_event.activated.connect(self.handle_ctrl_e_event)
        self.ctrl_slash_event = QShortcut(QKeySequence('Ctrl+/'), self)
        self.ctrl_slash_event.activated.connect(self.handle_ctrl_slash_event)
        self.ctrl_dot_event = QShortcut(QKeySequence('Ctrl+.'), self)
        self.ctrl_dot_event.activated.connect(self.handle_ctrl_dot_event)
        self.ctrl_less_than_event = QShortcut(QKeySequence('Ctrl+shift+,'), self)
        self.ctrl_less_than_event.activated.connect(self.handle_less_than_dot_event)
        self.ctrl_shift_o_event = QShortcut(QKeySequence('Ctrl+shift+o'), self)
        self.ctrl_shift_o_event.activated.connect(self.handle_ctrl_shift_o_event)

        #self.ctrl_plus_event = QShortcut(QKeySequence('Ctrl+Shift+='), self)
        #self.ctrl_plus_event.activated.connect(self.handle_ctrl_pluse_event)

        pybutton = QPushButton('Help', self)
        pybutton.clicked.connect(self.click_help)
        pybutton.resize(240,32)
        pybutton.move(40, 60)
    #ɔ
    def put_text_on_clipboard(self):
        x = 1
        text = self.line.text()
        clipboard = QtGui.QGuiApplication.clipboard()
        clipboard.setText(text)

    def handle_ctrl_shift_o_event(self):
        text = self.line.text()
        self.line.setText(text + 'ɔ')

    def on_open(self):
        print('Ctrl+o, dude!')# ʰ

    def handle_less_than_dot_event(self):
        text = self.line.text()
        last_letter = get_last_letter(text)
        if last_letter == 'o':
            text = if_last_char_is_x_replace_it_with_y(text, 'o', 'ô')#â
        if last_letter == 'a':
            text = if_last_char_is_x_replace_it_with_y(text, 'a', 'â')#âậ

        self.line.setText(text)

    def handle_ctrl_dot_event(self):
        text = self.line.text()
        last_letter = get_last_letter(text)
        if last_letter == 'd':
            text = if_last_char_is_x_replace_it_with_y(text, 'd', 'ḍ')
        elif last_letter == 's':
            text = if_last_char_is_x_replace_it_with_y(text, 's', 'ṣ')
        elif last_letter == 't':#
            text = if_last_char_is_x_replace_it_with_y(text, 't', 'ṭ')
        elif last_letter == 'z':
            text = if_last_char_is_x_replace_it_with_y(text, 'z', 'ẓ')#âậ
        elif last_letter == 'â':
            text = if_last_char_is_x_replace_it_with_y(text, 'â', 'ậ')#â

        self.line.setText(text)

    def handle_ctrl_slash_event(self):
        text = self.line.text()
        last_letter = get_last_letter(text)
        if last_letter == 'n':
            text = if_last_char_is_x_replace_it_with_y(text, 'n', 'ń')
        elif last_letter == 's':
            text = if_last_char_is_x_replace_it_with_y(text, 's', 'ś')
        elif last_letter == 'z':
            text = if_last_char_is_x_replace_it_with_y(text, 'z', 'ź')
        self.line.setText(text)

    def handle_ctrl_e_event(self):
        text = self.line.text()
        self.line.setText(text + 'ɛ')

    def handle_ctrl_o_event(self):
        text = self.line.text()
        self.line.setText(text + 'ɣ')

    def handle_ctrl_qmark_event(self):
        print('Ctrl+?, holmes!')
        text = self.line.text()
        #last_letter = get_last_letter(text)
        #if last_letter == '?':
        #    text = if_last_char_is_x_replace_it_with_y(text, '?', 'ʔ')
        self.line.setText(text + 'ʔ')

    def handle_ctrl_comma_event(self):
        x = 1
        print('ctrt+, baby!')
        text = self.line.text()
        last_letter = get_last_letter(text)
        if last_letter == 'n':
            text = if_last_char_is_x_replace_it_with_y(text, 'n', 'ŋ')
        self.line.setText(text)

    def handle_ctrl_plus_event(self):
        text = self.line.text()

        print('plus!!')
        #self.line.setText(text + 'ʰ')

    def handle_ctrl_h_event(self):
        text = self.line.text()
        self.line.setText(text + 'ʰ')

    def handle_alt_h_event(self):
        text = self.line.text()
        self.line.setText(text + 'ʰ')

    def handle_ctrl_b_event(self):
        text = self.line.text()
        self.line.setText(text + 'ᴮ')

    def handle_alt_b_event(self):
        text = self.line.text()
        self.line.setText(text + 'ᴮ')

    def handle_crtl_c_event(self):
        text = self.line.text()
        print('handle_crlt_c_event()')
        self.line.setText(text + 'ᶜ')

    def handle_alt_c_event(self):
        text = self.line.text()
        print('handle_alt_c_event()')
        self.line.setText(text + 'ᶜ')

    def handle_ctrl_f_event(self):
        text = self.line.text()
        last_letter = get_last_letter(text)
        if last_letter == 'a':
            text = if_last_char_is_x_replace_it_with_y(text, 'a', 'ɑ')
        elif last_letter == 'i':
            text = if_last_char_is_x_replace_it_with_y(text, 'i', 'ɨ')
        elif last_letter == 'e':
            text = if_last_char_is_x_replace_it_with_y(text, 'e', 'ə')
        self.line.setText(text)


            #    def eventFilter(self, event):
#        x = 1
#    def key_press_event(self, event):
#        x = 1
#        if event.type() == QtCore.QEvent.KeyPress:
#            print('QtCore.QEvent.KeyPress happened!')

#    def keyPressEvent(self, event):
#        #QtCore.QEvent.KeyPress
#        if event.key() == QtCore.Key_Space:
#            print('Space key')

    def showCurrentText(self, text):
        print('current-text:', text)
    #def keyPressEvent(self, e):
    #    print('key pressed == ' + str(e))
    #    if e.key() == QtCore.Key_F5:
    #        self.close()
    def click_help(self):
        x = 1
        #print('Your name: ' + self.line.text())
        open_txt_file_in_notepad(os.path.join(get_soas_code_dir(), 'ime', 'help_instructions.txt'))

def get_last_letter(text):
    retval = ''
    if text.strip():
        if len(text) == 1:
            retval = text
        elif len(text) > 1:
            retval = text[len(text)-1]
    return retval

def if_last_char_is_x_replace_it_with_y(text, x, y):
    if text.strip():
        if len(text) == 1:
            if text == x:
                text = y  # ɑ
        elif len(text) > 1:
            if text[len(text) - 1] == x:
                text = text[0:len(text) - 1] + y
    return text

def get_soas_code_dir():
    return os.path.join('D:' + os.sep + 'Ash', 'SOAS', 'code')

class state_memory:
    def __init__(self, filename):
        self.file = filename

    def remember_state(self, state):
        delete_file_if_it_exists(self.file)
        append_line_to_output_file(self.file, state)

    def recall_state(self):
        return readlines_of_utf8_file(self.file)[0]

def debug_msg(msg, origin, do_print_msg=False):
    output = ''
    if do_print_msg:
        if origin:
            output = origin + ' '
        output += msg
        print(output)

def file_does_exist(filename):
    retval = False
    if os.path.isfile(filename):
        retval = True
    return retval

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        ui_file = os.path.join(get_soas_code_dir(), 'ime', 'schuessler_ime.ui')
        if not file_does_exist(ui_file):
            debug_msg('ERROR: bad filename - ' + ui_file, 'Ui::__init__()', self.print_debug_msgs)
            return
        uic.loadUi(ui_file, self)
        self.class_name = 'Ui'
        self.print_debug_msgs = True
        self.do_print_debug_msg = True
#        self.data_type_gb_memory = state_memory(self.get_data_type_gb_memory_filename())

#        self.initialize_data_type_gb_connect_functions()
#        self.initialize_data_type_gb()

        self.show()

    def keyPressEvent(self, event):
        # Re-direct ESC key to closeEvent
        print(event)
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == QKeySequence.Copy:
            self.actionCopy.trigger()
    def eventFilter(self, widget, event):
        # u'The important thing to note is that the the event-filter should return
        #    True to stop any further handling,
        #    False to pass the event on for further handling, or otherwise just drop through to the base-class event-filter.'
        funct_name = 'Ui::eventFilter()'
        #print(funct_name)
        if event.type() == QtCore.QEvent.KeyPress:
            if QtGui.QKeySequence((event.key() + int(event.modifiers()))) == QtGui.QKeySequence("Ctrl+v"):
                print(funct_name + u' FULL SUCCESS!!! Captured Ctrl+v!!!')
                self.on_ctrl_v()
            elif QtGui.QKeySequence((event.key() + int(event.modifiers()))) == QtGui.QKeySequence("Ctrl+x"):
                print(funct_name + u' FULL SUCCESS!!! Captured Ctrl+x!!!')
                self.on_ctrl_x()

        return QtGui.QWidget.eventFilter(self, widget, event)
    def on_ctrl_v(self):
        print('Ctrl+v pressed!')
    def on_ctrl_x(self):
        print('Ctrl+x pressed!')

def open_txt_file_in_notepad(txt_file):
    funct_name = 'open_txt_file_in_notepad()'
    # from: https://stackoverflow.com/questions/636561/how-can-i-run-an-external-command-asynchronously-from-python
    if not txt_file:
        print(funct_name + u' ERROR: no .txt filename!')
        return
    subprocess.Popen(['notepad.exe', txt_file], stdout=PIPE, stderr=PIPE)

if 0:
    if __name__ == "__main__":
        app = QtWidgets.QApplication(sys.argv)
        window = Ui()
        app.exec_()
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit( app.exec_() )

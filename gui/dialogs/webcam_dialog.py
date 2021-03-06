import os

import cv2
from PyQt5 import QtGui, QtCore, QtWidgets
from simple_logger import Logger

import thermography as tg
from gui.design import Ui_WebCam


class WebcamDialog(QtWidgets.QMainWindow, Ui_WebCam):
    """Class representing the webcam dialog for webcam detection."""

    webcam_port_signal = QtCore.pyqtSignal(int)
    """Signal emitted by the current dialog when the webcam port has been detected."""

    def __init__(self, parent=None):
        """Initializes the current dialog and shows its view to the user."""
        super(self.__class__, self).__init__(parent=parent)
        Logger.info("Opened Webcam dialog")
        self.setupUi(self)
        self.__set_logo_icon()

        self.webcam_value = 0
        self.cap = cv2.VideoCapture(self.webcam_value)

        self.next_button.clicked.connect(self.__increase_webcam_value)
        self.previous_button.clicked.connect(self.__decrease_webcam_value)
        self.ok_button.clicked.connect(self.__current_webcam_value_found)

    def __set_logo_icon(self):
        gui_path = os.path.join(os.path.join(tg.settings.get_thermography_root_dir(), os.pardir), "gui")
        logo_path = os.path.join(gui_path, "img/logo-webcam.png")
        Logger.debug("Setting logo <{}>".format(logo_path))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(logo_path), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)

    def __increase_webcam_value(self):
        Logger.debug("Increasing webcam port value to {}".format(self.webcam_value + 1))
        self.webcam_value += 1
        self.previous_button.setEnabled(True)
        self.__set_webcam()

    def __decrease_webcam_value(self):
        Logger.debug("Decreasing webcam port value to {}".format(self.webcam_value - 1))
        self.webcam_value -= 1
        if self.webcam_value == 0:
            self.previous_button.setEnabled(False)
        self.__set_webcam()

    def __current_webcam_value_found(self):
        self.webcam_port_signal.emit(self.webcam_value)
        self.close()

    def __set_webcam(self):
        self.__stop()
        self.cap.release()
        self.cap = cv2.VideoCapture(self.webcam_value)
        self.__start()
        self.ok_button.setText("Use port {}!".format(self.webcam_value))

    def __start(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.__next_frame)
        self.timer.start(1000. / 30)

    def __next_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = QtGui.QImage(frame, frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888)
            pix = QtGui.QPixmap.fromImage(img)
            self.webcam_view.setPixmap(pix)
        else:
            font = QtGui.QFont()
            font.setPointSize(15)
            self.webcam_view.setFont(font)
            self.webcam_view.setAlignment(QtCore.Qt.AlignCenter)
            self.webcam_view.setText("No webcam found")

    def __stop(self):
        self.timer.stop()

    def deleteLater(self):
        self.cap.release()
        super(QtWidgets, self).deleteLater()

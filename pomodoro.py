from PyQt6.QtWidgets import *
from PyQt6.QtGui import QIcon, QCursor
from PyQt6 import uic
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput, QSoundEffect
from PyQt6.QtCore import Qt, QUrl
from designs import indexes
from data import *
import sys


class App(QMainWindow):
    def __init__(self) -> None:
        super(App, self).__init__()
        uic.loadUi(r"designs/design.ui", self)
        self.setWindowIcon(QIcon(r"icons/tomato.png"))

        # work with database
        self.db = DB()

        # widget attributes: stacked widget with all pages
        self.stacked = self.findChild(QStackedWidget, "stackedWidget")
        self.main_page = self.findChild(QWidget, "main_widget")

        # buttons
        self.menu_start = self.findChild(QPushButton, "menu_start")
        self.menu_settings = self.findChild(QPushButton, "menu_settings")
        self.menu_exit = self.findChild(QPushButton, "menu_exit")

        self.main_back = self.findChild(QPushButton, "from_main_to_menu")
        self.main_create = self.findChild(QPushButton, "create_new")

        self.settings_back = self.findChild(QPushButton, "from_st_to_menu")

        self.create_back = self.findChild(QPushButton, "from_cr_to_menu")
        self.create_do = self.findChild(QPushButton, "final_create")
        self.create_clear = self.findChild(QPushButton, "clear_fields")

        # click processing
        self.menu_start.clicked.connect(lambda: self.stacked.setCurrentIndex(indexes.c_main))
        self.menu_settings.clicked.connect(lambda: self.stacked.setCurrentIndex(indexes.c_settings))
        self.menu_exit.clicked.connect(lambda: self.close())

        self.main_back.clicked.connect(lambda: self.stacked.setCurrentIndex(indexes.c_menu))
        self.main_create.clicked.connect(lambda: self.stacked.setCurrentIndex(indexes.c_create))

        self.settings_back.clicked.connect(lambda: self.stacked.setCurrentIndex(indexes.c_menu))

        self.create_back.clicked.connect(lambda: self.stacked.setCurrentIndex(indexes.c_main))
        self.create_clear.clicked.connect(lambda: self.clearing())
        self.create_do.clicked.connect(lambda: self.add_session())

        # create block fields
        self.input_name = self.findChild(QTextEdit, "name_edit")
        self.radio1 = self.findChild(QRadioButton, "radio1")
        self.radio2 = self.findChild(QRadioButton, "radio2")
        self.radio3 = self.findChild(QRadioButton, "radio3")
        self.radio4 = self.findChild(QRadioButton, "radio4")

        # some work with layout for scroll area with work sessions
        self.scroll_area = self.findChild(QScrollArea, "scrollArea")
        self.grid_layout = QGridLayout(self.scroll_area)
        self.grid_layout.setObjectName(u"gridLayout")
        self.scroll_widget = self.findChild(QWidget, "scrollAreaWidgetContents")
        self.scroll_widget.setLayout(self.grid_layout)
        self.scroll_area.setWidget(self.scroll_widget)

        # show all sessions
        self.showing()

        self.vert_timer = self.findChild(QVBoxLayout, "vertical_timer")
        self.vert_task = self.findChild(QVBoxLayout, "vertical_task")
        self.hor_buttons = self.findChild(QHBoxLayout, "horizontal_buttons")

        # self.stop_session = self.findChild(QPushButton, "stop_session")
        # self.stop_session.clicked.connect(lambda: self.ses_return())
        #
        # self.start_timer = self.findChild(QPushButton, "start_timer")
        #
        self.music_flag = False
        self.start_audio = self.findChild(QPushButton, "start_audio")
        self.start_audio.clicked.connect(lambda: self.play_music())
        #
        # self.add_task = self.findChild(QPushButton, "add_task")
        #
        # self.task_frame = self.findChild(QLabel, "task_label")
        # self.task_frame.setAlignment(Qt.AlignmentFlag.AlignTop)
        # self.task_frame.setStyleSheet("color: #FFFFFF; font-family: 'Courier New';")
        # self.task_frame.setWordWrap(True)
        # self.task_text = self.findChild(QPlainTextEdit, "task_edit")
        # self.task_text.setPlainText('')
        # self.task_text.setPlaceholderText("Введіть поточне завдання")
        #
        # self.box = self.findChild(QGroupBox, "groupBox_12")

    def showing(self) -> None:
        # clearing for fast updating
        while self.grid_layout.count() > 0:
            self.grid_layout.itemAt(0).widget().setParent(None)

        # some work with data
        self.sessions = self.db.get_all()
        length = len(self.sessions)
        rows = (length // 4) + 1 if length % 4 != 0 else (length // 4)
        columns, number, current = 4, 0, 0

        # loop for creating frames of sessions
        for i in range(rows):
            for j in range(number, columns):
                if length > 0:
                    session = self.sessions[current]

                    self.frame = QFrame(self.scroll_widget)
                    self.frame.setObjectName("frame_" + str(session[0]))
                    self.frame.setMinimumWidth(120)
                    self.frame.setMinimumHeight(200)
                    self.frame.setStyleSheet("background-color: #944743; color: #ffffff; margin:10px; padding: 0px;")

                    self.vert_layout = QVBoxLayout(self.frame)
                    self.vert_layout.setObjectName("vert_layout")

                    self.ses_name = QLabel()
                    self.ses_name.setWordWrap(True)
                    self.ses_name.setText(f"{session[1]}")
                    self.ses_name.setStyleSheet("margin: 0px;")
                    self.ses_name.setAlignment(Qt.AlignmentFlag.AlignCenter)

                    self.description = QLabel()
                    self.description.setWordWrap(True)
                    self.description.setText(f"Created: {session[2]}\n"
                                             f"To work: {session[-2]} mins\nFree time: {session[-1]} mins")
                    self.description.setStyleSheet("margin: 0px;padding:5px;")

                    self.btn_delete = QPushButton()
                    self.btn_delete.setObjectName("btn_delete" + str(session[0]))


                    self.btn_delete.setText("Видалити")
                    self.btn_delete.setStyleSheet("margin: 0px;")
                    self.btn_delete.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                    self.btn_delete.clicked.connect(lambda ch, text=self.frame.objectName():
                                                    self.delete_ses(text.split("_")[1]))

                    self.btn_start = QPushButton()
                    self.btn_start.setText("Розпочати")
                    self.btn_start.setStyleSheet("margin: 0px;")
                    self.btn_start.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                    self.btn_start.clicked.connect(lambda ch, text=self.frame.objectName():
                                                    self.start_ses(text.split("_")[1]))

                    self.vert_layout.addWidget(self.ses_name)
                    self.vert_layout.addWidget(self.description)
                    self.vert_layout.addWidget(self.btn_delete)
                    self.vert_layout.addWidget(self.btn_start)

                    self.grid_layout.addWidget(self.frame, i, j, 1, 1, Qt.AlignmentFlag.AlignHCenter |
                                               Qt.AlignmentFlag.AlignVCenter)
                    length, current = length - 1, current + 1
                else:
                    break
            if length == 0:
                break

    def delete_ses(self, ses_id: int) -> None:
        result = QMessageBox.question(self, "Підтвердження видалення",
                                            "Вы дійсно хочете видалити цю сесію?",
                                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                            QMessageBox.StandardButton.No)
        if result == QMessageBox.StandardButton.Yes:
            self.db.delete_session(ses_id)
            self.showing()
            self.scroll_area.verticalScrollBar().setValue(
                self.scroll_area.verticalScrollBar().minimum()
            )

    def start_ses(self, ses_id: int, flag=False) -> None:
        # clearing for fast updating
        while self.vert_task.count() > 0:
            self.vert_task.itemAt(0).widget().setParent(None)
        while self.hor_buttons.count() > 0:
            self.hor_buttons.itemAt(0).widget().setParent(None)

        self.ses_period = QLabel()
        self.ses_period.setObjectName(f"period_{ses_id}")
        self.ses_period.setStyleSheet("color: #ffffff;")
        self.ses_period.setMinimumHeight(30)

        self.task_text = QLabel()
        self.task_text.setObjectName(f"text_{ses_id}")
        self.task_text.setWordWrap(True)
        self.task_text.setStyleSheet("color: #ffffff;")
        self.task_text.setMinimumHeight(80)
        self.task_text.setAlignment(Qt.AlignmentFlag.AlignTop)

        result = self.db.get_task(ses_id)
        self.task_text.setText(result)

        self.task_edit = QPlainTextEdit()
        self.task_edit.setObjectName(f"edit_{ses_id}")
        self.task_edit.setPlaceholderText("Введіть поточне завдання")
        self.task_edit.setStyleSheet("background-color: #e2e2e2; border-radius: 5px;")
        self.task_edit.setMinimumHeight(50)

        self.vert_task.addWidget(self.ses_period)
        self.vert_task.addWidget(self.task_text)
        self.vert_task.addWidget(self.task_edit)

        # adding buttons
        self.ses_back = QPushButton()
        self.ses_back.setText("Повернутись")
        self.ses_back.clicked.connect(lambda: self.ses_return())
        self.ses_back.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.start_timer = QPushButton()
        self.start_timer.setObjectName(f"start_{ses_id}")
        self.start_timer.setText("Почати")
        # self.start_timer.clicked.connect()
        self.start_timer.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.updating_task = QPushButton()
        self.updating_task.setObjectName(f"start_{ses_id}")
        self.updating_task.setText("Оновити завдання")
        self.updating_task.clicked.connect(lambda ch, idx=self.updating_task.objectName().split("_")[1]:
                                           self.update_task(int(idx)))
        self.updating_task.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.hor_buttons.addWidget(self.ses_back)
        self.hor_buttons.addWidget(self.start_timer)
        self.hor_buttons.addWidget(self.updating_task)

        # converting data into a dict
        self.session_data = self.db.get_one(ses_id)
        key_values = ['id', 'name', 'date', 'worktime', 'freetime']
        self.dict_data = dict(zip(key_values, *self.session_data))

        self.name_label = self.findChild(QLabel, "sesname")
        self.name_label.setText(self.dict_data['name'])
        self.name_label.setStyleSheet("color: #ffffff; font-family: 'Courier New'; font-size: 14px")

        data_task = self.db.get_task(ses_id)
        #self.task_frame.setText(data_task)

        #self.btn_task = self.findChild(QPushButton, "add_task")
        #self.btn_task.clicked.connect(lambda ch, idx=self.dict_data['id']: self.update_task(idx))
        self.stacked.setCurrentIndex(indexes.c_timer)

    def ses_return(self):
        if self.music_flag:
            self.player.pause()
            self.music_flag = False
        self.stacked.setCurrentIndex(indexes.c_main)

    def update_task(self, ses_id: int):
        task = self.task_edit.toPlainText()
        print(f"'id {ses_id}: {task}'")
        self.db.update_task(ses_id, task)
        self.start_ses(ses_id)

        self.task_edit.setPlainText('')

    def play_music(self) -> None:
        if self.music_flag:
            self.player.pause()
            self.music_flag = False
        else:
            filename = f"audio/lofi.mp3"
            self.player = QMediaPlayer()
            self.audio_output = QAudioOutput()
            self.player.setAudioOutput(self.audio_output)
            self.player.setSource(QUrl.fromLocalFile(filename))
            self.audio_output.setVolume(0.5)
            self.player.play()
            self.music_flag = True

    def clearing(self) -> None:
        self.input_name.setText("")
        self.radio1.setChecked(True)

    def add_session(self) -> None:
        name = self.input_name.toPlainText()
        radios = {"radio1": [20, 5], "radio2": [25, 5], "radio3": [35, 10], "radio4": [45, 15]}
        if not name:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Помилка створення")
            dlg.setIcon(QMessageBox.Icon.Critical)
            dlg.setText("Вам потрібно вказати назву сесії!")
            dlg.exec()
            return None
        for i in range(1, 5):
            selected_radio = self.findChild(QRadioButton, f"radio{i}")
            if selected_radio.isChecked():
                self.db.create_session(self.input_name.toPlainText(), radios[f"radio{i}"])
                self.showing()
                dlg = QMessageBox(self)
                dlg.setWindowTitle("Успішне створення")
                dlg.setText(f'Ви створили сесію "{name}"!')
                dlg.exec()
                self.clearing()

    def closeEvent(self, event) -> None:
        self.db.exit()
        event.accept()


def main():
    application = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(application.exec())


if __name__ == "__main__":
    main()

from PyQt6.QtWidgets import *
from PyQt6.QtGui import QIcon, QCursor, QTextCursor
from PyQt6 import uic
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import Qt, QUrl, QTimer, QPoint
from designs import indexes
from data import *
import sys
import notifications as nt


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
        self.stacked.setCurrentIndex(indexes.c_menu)

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

        self.music_flag = False
        self.start_audio = self.findChild(QPushButton, "start_audio")
        self.start_audio.clicked.connect(lambda: self.play_music())
        self.timer_flag = 0
        self.timer_started = False

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
        # converting data into a dict
        self.session_data = self.db.get_one(ses_id)
        key_values = ['id', 'name', 'date', 'worktime', 'freetime']
        self.dict_data = dict(zip(key_values, *self.session_data))

        self.ses_period = QLabel()
        self.ses_period.setObjectName(f"period_{ses_id}")
        self.ses_period.setStyleSheet("color: #ffffff; font-size: 16px; font-family: 'Courier New';")
        self.ses_period.setMinimumHeight(30)
        self.ses_period.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # clearing for fast updating
        while self.vert_task.count() > 0:
            self.vert_task.itemAt(0).widget().setParent(None)
        while self.hor_buttons.count() > 0:
            self.hor_buttons.itemAt(0).widget().setParent(None)

        if not flag:
            self.only_timer(ses_id)

        self.task_text = QLabel()
        self.task_text.setObjectName(f"text_{ses_id}")
        self.task_text.setWordWrap(True)
        self.task_text.setStyleSheet("color: #ffffff; padding: 2px;")
        self.task_text.setMinimumHeight(80)
        self.task_text.setAlignment(Qt.AlignmentFlag.AlignTop)

        result = self.db.get_task(ses_id)
        self.task_text.setText(result)

        self.task_edit = QPlainTextEdit()
        self.task_edit.setObjectName(f"edit_{ses_id}")
        self.task_edit.setPlaceholderText("Введіть поточне завдання")
        self.task_edit.setStyleSheet("background-color: #e2e2e2; border-radius: 5px;")
        self.task_edit.setMinimumHeight(50)
        self.task_edit.textChanged.connect(lambda: self.text_checking())

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
        self.start_timer.clicked.connect(lambda ch, idx=self.start_timer.objectName().split("_")[1]:
                                           self.begin_work(int(idx)))
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

        self.name_label = self.findChild(QLabel, "sesname")
        self.name_label.setText(self.dict_data['name'])
        self.name_label.setStyleSheet("color: #ffffff; font-family: 'Courier New'; font-size: 16px;"
                                      "font-weight: bold;")
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.stacked.setCurrentIndex(indexes.c_timer)

    def text_checking(self) -> None:
        if len(self.task_edit.toPlainText()) >= 90:
            self.task_edit.setPlainText(self.task_edit.toPlainText()[:-1])
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Помилка введення")
            dlg.setIcon(QMessageBox.Icon.Critical)
            dlg.setText("Ви намагаєтесь додати занадто довге завдання!")
            dlg.exec()

    def ses_return(self) -> None:
        if self.music_flag:
            self.player.pause()
            self.music_flag = False
        if self.timer_started:
            self.main_timer.stop()
            self.timer_started = False
        self.timer_flag = 0
        self.stacked.setCurrentIndex(indexes.c_main)

    def update_task(self, ses_id: int) -> None:
        task = self.task_edit.toPlainText() or "Немає завдань"
        self.db.update_task(ses_id, task)
        self.start_ses(ses_id)
        self.task_edit.setPlainText('')

    def only_timer(self, ses_id: int) -> None:
        while self.vert_timer.count() > 0:
            self.vert_timer.itemAt(0).widget().setParent(None)
        self.timer = QLabel()
        self.timer.setObjectName(f"timer_{ses_id}")
        self.timer.setStyleSheet("color: #121212; font-weight: bold; font-size: 50px;"
                                 "font-family: 'Courier New'")
        self.timer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # seconds_left
        if not self.timer_started:
            self.mins, self.seconds = self.dict_data['worktime'], 0
        self.timer.setText(f"{self.mins:02}:{self.seconds:02}")
        self.ses_period.setText("Роботу не почато" if not self.timer_started else
                                "Працюйте!" if not self.timer_flag else "Відпочивайте!")

        self.vert_timer.addWidget(self.timer)

    def show_time(self, ses_id: int, worktime: int, freetime: int) -> None:
        # worktime and freetime in seconds
        if self.left > 0:
            self.show_current(ses_id)
            self.left -= 1
        else:
            self.timer_flag = 1 if self.timer_flag == 0 else 0
            nt.Notification().send(self.timer_flag)
            self.left = freetime if self.timer_flag else worktime
            self.ses_period.setText("Працюйте!" if not self.timer_flag else "Відпочивайте!")
            self.show_current(ses_id)

    def show_current(self, ses_id: int) -> None:
        self.total = self.left
        self.mins = self.total // 60
        self.seconds = self.total - self.mins * 60
        self.only_timer(ses_id)

    def begin_work(self, ses_id: int) -> None:
        nt.Notification().send(0)
        self.timer_started = True
        self.timer_data = list(map(int, self.db.get_time(ses_id).split()))
        self.reference = dict(zip(['work', 'free'], self.timer_data))
        self.starting = [self.reference['work'] * 60, self.reference['free'] * 60]
        self.left = self.starting[0] if not self.timer_flag else self.starting[1]

        self.main_timer = QTimer()
        self.main_timer.setObjectName(f"timer_{ses_id}")
        self.main_timer.setInterval(1000)
        self.main_timer.timeout.connect(lambda: self.show_time(ses_id, *self.starting))
        self.main_timer.start()

        self.left_seconds = self.reference

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

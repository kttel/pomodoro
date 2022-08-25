from plyer import notification
from random import choice


class Notification:
    modes = {0: "працювати", 1: "відпочивати"}
    arr_free = ['попити води', 'зробити перекус', 'подивитись у вікно', 'пройтись по кімнаті']
    arr_work = ['продовжити роботу', 'виконувати завдання', 'вдосконалюватись']

    @classmethod
    def send(cls, mode):
        action = cls.modes[mode]
        additional_text = choice(cls.arr_free) if mode else choice(cls.arr_work)

        notification.notify(
            title='Pomodoro tracker',
            message=f'Час {action} та {additional_text}!',
            app_icon=r'icons/tomato.ico',
            timeout=10,
        )
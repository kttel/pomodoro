from plyer import notification


class Notification():
    modes = {0: "працювати", 1: "відпочивати"}

    @classmethod
    def send(cls, mode):
        action = cls.modes[mode]
        notification.notify(
            title='Pomodoro tracker',
            message=f'Час {action}',
            app_icon=r'icons/tomato.ico',
            timeout=10,
        )
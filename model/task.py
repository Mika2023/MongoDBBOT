from datetime import datetime,timedelta,date,time


class Task:
    def __init__(self):
        self.id = 0
        self.text = ""
        self.deadline = datetime(2025,1,1,00,00)
        self.isCompleted = False

    def timeLeft(self):
        now_time = datetime.now()
        return self.deadline-now_time

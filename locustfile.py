from locust import HttpUser, task, between
import random

class BotUser(HttpUser):
    wait_time = between(1, 3)  # Задержка между запросами

    @task(3)  # Частота выполнения задачи (3 к 1)
    def send_start(self):
        # Эмуляция команды /start
        self.client.post(
            "/webhook",  # Путь, куда Telegram отправляет обновления
            json={
                "message": {
                    "chat": {"id": random.randint(1, 10000)},
                    "text": "/start"
                }
            }
        )

    @task(1)
    def next_lesson(self):
        # Эмуляция нажатия кнопки "Следующий урок"
        self.client.post(
            "/webhook",
            json={
                "callback_query": {
                    "data": "next_lesson",
                    "message": {"chat": {"id": random.randint(1, 10000)}}
                }
            }
        )
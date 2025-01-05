import openai
from PyQt5.QtCore import QRunnable


class ChatGPT(QRunnable):
    def __init__(self, api_key, question, signal):
        super().__init__()
        self.api_key = api_key
        self.question = question
        self.signal = signal

    def run(self):
        openai.api_key = self.api_key
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": self.question}
                ]
            )
            reply = response['choices'][0]['message']['content']
        except Exception as e:
            reply = f"Error: {str(e)}"
        self.signal.response_signal.emit(reply)

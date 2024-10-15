import openai
from PyQt5.QtCore import QThread, pyqtSignal


class ChatGPT(QThread):
    response_signal = pyqtSignal(str)

    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key
        self.question = ""
        self.running = True

    def run(self):
        openai.api_key = self.api_key
        while self.running:
            if self.question:
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo-16k",
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant."},
                            {"role": "user", "content": self.question}
                        ]
                    )
                    reply = response['choices'][0]['message']['content']
                except Exception as e:
                    reply = f"Error: {str(e)}"

                self.response_signal.emit(reply)
                self.question = ""
                self.sleep(5)


    def ask_chatgpt(self, question):
        self.question = question

    def stop(self):
        self.running = False
        self.quit()
        self.wait()
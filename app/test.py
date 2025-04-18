import sys
import json
import base64
from PySide6.QtCore import QUrl, QByteArray, Qt
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
from res.paths import IMG_PATH


class GeminiClient(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Gemini Client")
        self.setGeometry(100, 100, 400, 200)

        # Set up the UI layout
        layout = QVBoxLayout()
        self.label = QLabel("Click the button to start request.")
        layout.addWidget(self.label)

        self.button = QPushButton("Send Request")
        self.button.clicked.connect(self.trigger_request)
        layout.addWidget(self.button)

        self.setLayout(layout)

        # Set up network manager
        self.network_manager = QNetworkAccessManager(self)
        self.network_manager.finished.connect(self.handle_response)

    def trigger_request(self):
        self.label.setText('Loading...')

        # Select what type of request you want to trigger
        request_type = "generate_content"  # Can be "generate_content" or "get_user_data"

        if request_type == "generate_content":
            self.send_generate_content_request()
        elif request_type == "get_user_data":
            self.send_get_user_data_request()
        else:
            self.label.setText("Unknown request type.")

    def send_generate_content_request(self):
        # Read and encode the image
        try:
            with open(IMG_PATH + 'screenshot.png', 'rb') as img_file:
                img_data = base64.b64encode(img_file.read()).decode('utf-8')
        except Exception as e:
            self.label.setText(f"Error reading image: {e}")
            return

        # Prepare POST request data for generating content
        model = "your-model-id"
        prompt = "Your input prompt"
        key = "your-api-key"

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
        headers = {'Content-Type': 'application/json'}
        data = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": img_data
                        }
                    }
                ]
            }]
        }

        # Prepare the request
        request = QNetworkRequest(QUrl(url))
        for header, value in headers.items():
            request.setRawHeader(header.encode(), value.encode())

        json_data = json.dumps(data).encode('utf-8')

        # Set a custom property to identify the request
        request.setProperty("request_type", "generate_content")

        # Send the POST request asynchronously
        self.network_manager.post(request, QByteArray(json_data))

    def send_get_user_data_request(self):
        # Example of another type of request (GET request for user data)
        url = "https://jsonplaceholder.typicode.com/users/1"  # Example URL
        request = QNetworkRequest(QUrl(url))

        # Set a custom property to identify this request
        request.setProperty("request_type", "get_user_data")

        # Send the GET request asynchronously
        self.network_manager.get(request)

    def handle_response(self, reply: QNetworkReply):
        # Retrieve the custom property set on the request to identify it
        request_type = reply.request().property("request_type")

        if reply.error() != QNetworkReply.NoError:
            self.label.setText(f"Error: {reply.errorString()}")
        else:
            response_data = reply.readAll()
            response_str = str(response_data, "utf-8")

            # Handle different types of responses based on request_type
            if request_type == "generate_content":
                self.handle_generate_content_response(response_str)
            elif request_type == "get_user_data":
                self.handle_get_user_data_response(response_str)
            else:
                self.label.setText("Unknown request type in response.")

        reply.deleteLater()

    def handle_generate_content_response(self, response_str):
        try:
            response_json = json.loads(response_str)
            text_content = response_json['candidates'][0]['content']['parts'][0]['text']
            self.label.setText(f"Generated Content: {text_content}")
        except Exception as e:
            self.label.setText(f"Error processing generate content response: {e}")

    def handle_get_user_data_response(self, response_str):
        try:
            response_json = json.loads(response_str)
            user_name = response_json['name']  # Example response field
            self.label.setText(f"User Data: {user_name}")
        except Exception as e:
            self.label.setText(f"Error processing user data response: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = GeminiClient()
    window.show()

    sys.exit(app.exec())

import base64
import requests

# Read the OpenAI API key from a file
with open("../gpt_key.txt") as keyFile:
    api_key = keyFile.read().strip()

def encode_image(image_path):
    """
    Encode an image to base64 format.

    Args:
        image_path (str): The path to the image file.

    Returns:
        str: Base64 encoded string of the image.
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

class Message:
    def __init__(self, text, role="user", imgPaths=None):
        """
        Initialize a Message instance.

        Args:
            text (str): The text content of the message.
            role (str): The role of the message sender (default is "user").
            imgPaths (list): List of image paths to be included in the message (default is None).
        """
        self.role = role
        self.text = text
        self.imgPaths = imgPaths or []
        self.imgStrings = [encode_image(imgPath) for imgPath in self.imgPaths]

    def toJSON(self):
        """
        Convert the Message instance to a JSON serializable format.

        Returns:
            dict: JSON serializable dictionary representation of the message.
        """
        msg = {"role": self.role, "content": [{"type": "text", "text": self.text}]}
        for img in self.imgStrings:
            msg["content"].append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img}"}})
        return msg

class Conversation:
    def __init__(self, headers=None, payload=None):
        """
        Initialize a Conversation instance.

        Args:
            headers (dict): HTTP headers for the API request (default is None).
            payload (dict): Payload for the API request (default is None).
        """
        self.conversation = []
        self.headers = headers or {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        self.payload = payload or {
            "model": "gpt-4o",
            "max_tokens": 500,
            "messages": []
        }

    def speak(self, message):
        """
        Send a message in the conversation and get the response.

        Args:
            message (Message): The message to be sent.

        Returns:
            str: The text content of the GPT model's response.
        """
        self.conversation.append(message)
        msg = message.toJSON()
        self.payload["messages"].append(msg)

        # Make the API request to OpenAI
        reply = requests.post("https://api.openai.com/v1/chat/completions", headers=self.headers, json=self.payload).json()
        
        # Create and append the GPT response message
        gpt_message = Message(reply["choices"][0]["message"]["content"], role=reply["choices"][0]["message"]["role"])
        self.payload["messages"].append(gpt_message.toJSON())
        self.conversation.append(gpt_message)

        print(gpt_message.text + "\n____________________________\n\n")
        return gpt_message.text

    def copy(self):
        """
        Create a copy of the current conversation instance.

        Returns:
            Conversation: A new Conversation instance with the same headers and payload.
        """
        return Conversation(headers=self.headers, payload=self.payload)

from Conversation import *
import numpy as np
import cv2
import base64

# Prompt for generating hotspots
hotspots_prompt = '''This photo was taken to be used in a visual screen display for a child.
The child using the visual screen display is pre-linguistic, they haven't begun to communicate verbally.
Please provide relevant hotspots (simplified as best you can!) in the image with accompanying contextually
relevant communication options if you are focused on building engagement in interactions and the emergence of words.
Only respond with the hotspot names and options, nothing more! Structure your response like the following:
Hotspot 1: Hotspot
- Option 1: Option
- Option 2: Option
etc.'''

class Hotspot:
    def __init__(self, hotspotName='', options=None):
        """
        Initialize a Hotspot instance.

        Args:
            hotspotName (str): The name of the hotspot (default is empty string).
            options (list): List of options associated with the hotspot (default is None).
        """
        self.hotspotName = hotspotName
        self.options = options or []

    def __str__(self):
        return f"{self.hotspotName}: {self.options}"

    def toJSON(self):
        """
        Convert the Hotspot instance to a JSON serializable format.

        Returns:
            dict: JSON serializable dictionary representation of the hotspot.
        """
        return {"hotspotName": self.hotspotName, "options": self.options}

def write_image(fileName, image_data):
    """
    Write a base64 encoded image to a file.

    Args:
        fileName (str): The name of the file to save the image.
        image_data (str): The base64 encoded image data.
    """
    if image_data.startswith('data:image/png;base64,'):
        image_data = image_data.replace('data:image/png;base64,', '')
    
    # Decode the base64 string
    decoded_data = base64.b64decode(image_data)
    
    # Convert the byte data to a numpy array
    np_arr = np.frombuffer(decoded_data, np.uint8)
    
    # Decode the numpy array to an image
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    
    # Save the image
    cv2.imwrite(fileName, image)

def parse_hotspots(gpt_response):
    """
    Parse the GPT response to extract hotspots and options.

    Args:
        gpt_response (str): The GPT response text.

    Returns:
        list: List of Hotspot instances.
    """
    lines = gpt_response.split('\n')
    hotspots = []
    currHotspot = None

    for line in lines:
        lower_line = line.lower()
        if "hotspot" in lower_line and ":" in lower_line:
            if currHotspot:
                hotspots.append(currHotspot)
            hotspot_name = line.split(": ", 1)[1]
            currHotspot = Hotspot(hotspotName=hotspot_name)
        elif "option" in lower_line and ":" in lower_line:
            option = line.split(": ", 1)[1]
            if currHotspot:
                currHotspot.options.append(option)
    
    if currHotspot:
        hotspots.append(currHotspot)
    
    return hotspots

def generate_hotspots(user_img_url):
    """
    Generate hotspots for a given image URL using GPT.

    Args:
        user_img_url (str): The URL of the user's image.

    Returns:
        list: List of Hotspot instances.
    """
    conversation = Conversation()
    conversation.speak(Message(hotspots_prompt, imgPaths=[user_img_url]))
    gpt_response_text = conversation.conversation[-1].text
    hotspots = parse_hotspots(gpt_response_text)
    return hotspots

from flask import Flask, request, jsonify
from flask_cors import CORS
from main import *
import json

app = Flask(__name__)
CORS(app)

# Path to save the user image
user_img_url = "./userImage.png"

@app.route('/api/send-data', methods=['POST'])
def receive_data():
    """
    Endpoint to receive image data, process it to generate hotspots,
    and return the hotspots as JSON response.

    Returns:
        Response: JSON response containing the hotspots.
    """
    image_data = request.json  # Assuming JSON data is sent
    write_image(user_img_url, image_data)
    
    hotspots = generate_hotspots(user_img_url)
    
    # Print each hotspot's JSON representation for debugging
    for hs in hotspots:
        print(hs.toJSON())

    # Return the hotspots as a JSON response
    return jsonify([hs.toJSON() for hs in hotspots])

@app.route('/api/send-VSD', methods=['POST'])
def receive_VSD():
    """
    Endpoint to receive VSD data and save it to a file.

    Returns:
        str: Success message.
    """
    with open("sampleVSD.json", "w") as VSD:
        json.dump(request.json, VSD)
    return "VSD data received and saved."

if __name__ == '__main__':
    app.run()

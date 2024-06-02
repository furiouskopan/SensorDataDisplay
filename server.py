from flask import Flask, request, render_template
from flask_socketio import SocketIO, emit
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)
socketio = SocketIO(app)

# Define the path to the CSV file
csv_file_path = 'sensor_data.csv'

# Initialize the CSV file with headers if it does not exist
def init_csv_file():
    if not os.path.isfile(csv_file_path):
        df = pd.DataFrame(columns=['timestamp', 'aqi_value', 'x', 'y', 'z'])
        df.to_csv(csv_file_path, index=False)

init_csv_file()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/post_data_endpoint', methods=['POST'])
def post_data():
    try:
        aqi_value = float(request.form['aqiValue'])
        x = float(request.form['x'])
        y = float(request.form['y'])
        z = float(request.form['z'])
    except ValueError as e:
        return f"Error: {e}"

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Append data to the CSV file
    with open(csv_file_path, 'a') as f:
        f.write(f'{timestamp},{aqi_value},{x},{y},{z}\n')

    # Emit the sensor data to all connected clients
    socketio.emit('sensor_data', {'aqi_value': aqi_value, 'x': x, 'y': y, 'z': z})
    
    return f"Data received: AQI={aqi_value}, X={x}, Y={y}, Z={z}"

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)

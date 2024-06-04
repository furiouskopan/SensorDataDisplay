from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import csv
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sensor_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
socketio = SocketIO(app)

# # Define the path to the CSV file
# csv_file_path = 'sensor_data.csv'

# # Initialize the CSV file with headers if it does not exist
# def init_csv_file():
#     if not os.path.isfile(csv_file_path):
#         df = pd.DataFrame(columns=['timestamp', 'aqi_value', 'x', 'y', 'z'])
#         df.to_csv(csv_file_path, index=False)

init_csv_file()

class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    aqi_value = db.Column(db.Float, nullable=False)
    accel_x = db.Column(db.Float, nullable=False)
    accel_y = db.Column(db.Float, nullable=False)
    accel_z = db.Column(db.Float, nullable=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/post_data_endpoint', methods=['POST'])
def post_data():
    try:
        aqi_value = float(request.form['aqiValue'])
        accel_x = float(request.form['x'])
        accel_y = float(request.form['y'])
        accel_z = float(request.form['z'])

        # Save to database
        sensor_data = SensorData(aqi_value=aqi_value, accel_x=accel_x, accel_y=accel_y, accel_z=accel_z)
        db.session.add(sensor_data)
        db.session.commit()

        # Emit data to clients
        socketio.emit('sensor_data', {
            'aqi_value': aqi_value,
            'x': accel_x,
            'y': accel_y,
            'z': accel_z
        })

        return "Data received and stored", 200
    except Exception as e:
        return f"Error: {str(e)}", 400

@app.route('/data', methods=['GET'])
def get_data():
    data = SensorData.query.all()
    result = [
        {
            'timestamp': d.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'aqi_value': d.aqi_value,
            'accel_x': d.accel_x,
            'accel_y': d.accel_y,
            'accel_z': d.accel_z
        } for d in data
    ]
    return jsonify(result)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, host='0.0.0.0', port=5000)

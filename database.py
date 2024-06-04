from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False)
    aqi_value = db.Column(db.Float, nullable=False)
    accel_x = db.Column(db.Float, nullable=False)
    accel_y = db.Column(db.Float, nullable=False)
    accel_z = db.Column(db.Float, nullable=False)

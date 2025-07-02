from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from bson.errors import InvalidId
import os
from pymongo.errors import ConnectionFailure
 
app = Flask(__name__)
CORS(app)
 
#Added the DB URI in the Render's environment
MONGO_URI = os.environ.get("MONGO_URI")
app.config["MONGO_URI"] = MONGO_URI
mongo = PyMongo(app)
 
#Trying the connection with MongoDB
try:
    mongo.cx.server_info()
    print("MongoDB connected successfully.")
except ConnectionFailure as e:
    print("MongoDB connection failed:", e)
    exit(1)
 
schedules_collection = mongo.db.schedules
 
 
#Creating the POST request for doctor's schedule
@app.route("/api/schedule/create", methods=["POST"])
def create_schedule():
    data = request.get_json()
 
    required_fields = ["doctor_id", "day", "start_time", "end_time"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
 
    result = schedules_collection.insert_one({
        "doctor_id": data["doctor_id"],
        "day": data["day"],
        "start_time": data["start_time"],
        "end_time": data["end_time"]
    })
 
    return jsonify({
        "message": "ZYour schedule got created successfully",
        "schedule_id": str(result.inserted_id)
    }), 201
 
 
# GET request to show the schedule on the dashboard
@app.route("/api/schedule/<doctor_id>", methods=["GET"])
def get_doctor_schedule(doctor_id):
    schedules = list(schedules_collection.find({"doctor_id": doctor_id}))
 
    if not schedules:
        return jsonify({"message": "Sorry, you have not aaded your schedule yet."}), 404
 
    result = []
    for s in schedules:
        result.append({
            "schedule_id": str(s["_id"]),
            "day": s["day"],
            "start_time": s["start_time"],
            "end_time": s["end_time"]
        })
 
    return jsonify(result), 200
 
 
#Creating PUT request to allow doctor's to update their schedule
@app.route("/api/schedule/update/<schedule_id>", methods=["PUT"])
def update_schedule(schedule_id):
    data = request.get_json()
 
    if not data:
        return jsonify({"error": "You have not added the message. Please enter the correct format"}), 400
 
    update_fields = {}
    allowed_fields = ["day", "start_time", "end_time"]
    for field in allowed_fields:
        if field in data:
            update_fields[field] = data[field]
 
    if not update_fields:
        return jsonify({"error": "Please provide valid field"}), 400
 
    try:
        result = schedules_collection.update_one(
            {"_id": ObjectId(schedule_id)},
            {"$set": update_fields}
        )
    except InvalidId:
        return jsonify({"error": "Invalid schedule ID"}), 400
 
    if result.matched_count == 0:
        return jsonify({"error": "You haven't created your schedule yet"}), 404
 
    return jsonify({"message": "Your schedule updated successfully."}), 200
 
 
#Creating DELETE API, if doctor's want to delete their schedule
@app.route("/api/schedule/delete/<schedule_id>", methods=["DELETE"])
def delete_schedule(schedule_id):
    try:
        result = schedules_collection.delete_one({"_id": ObjectId(schedule_id)})
    except InvalidId:
        return jsonify({"error": "Invalid schedule ID"}), 400
 
    if result.deleted_count == 0:
        return jsonify({"error": "You haven't created your schedule yet"}), 404
 
    return jsonify({"message": "Your schedule deleted successfully."}), 200
 
 
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
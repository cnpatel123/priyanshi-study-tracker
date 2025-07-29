# mongo_connector.py

from pymongo import MongoClient
import pandas as pd
from datetime import datetime
from bson.objectid import ObjectId

# ---- CONFIGURATION ----
# Replace <password> and <your-cluster> with your actual MongoDB Atlas password and cluster details
MONGO_URI = "mongodb+srv://cnpatel123:cnpatel12345@studytracker.xer6ru9.mongodb.net/?retryWrites=true&w=majority&appName=Studytracker"

DB_NAME = "studytracker_db"

def get_client():
    """Create and return a MongoDB client."""
    return MongoClient(MONGO_URI)

def get_collection(collection_name):
    """Return a MongoDB collection handle."""
    client = get_client()
    return client[DB_NAME][collection_name]

# ---- STUDY RECORDS ----

def add_study_record(date, subject, chapter, book_material, hours_studied, remarks):
    col = get_collection("study_records")
    col.insert_one({
        "date": str(date),
        "subject": subject,
        "chapter": chapter,
        "book_material": book_material,
        "hours_studied": hours_studied,
        "remarks": remarks,
        "created_at": datetime.now()
    })

def get_study_records():
    col = get_collection("study_records")
    df = pd.DataFrame(list(col.find()))
    if not df.empty and "_id" in df:
        df["_id"] = df["_id"].astype(str)
    return df

def delete_study_record(record_id):
    col = get_collection("study_records")
    col.delete_one({"_id": ObjectId(record_id)})

# ---- EXAM RECORDS ----

def add_exam_record(exam_date, subject, exam_type, maximum_marks, marks_scored, improvements):
    col = get_collection("exam_records")
    col.insert_one({
        "exam_date": str(exam_date),
        "subject": subject,
        "exam_type": exam_type,
        "maximum_marks": maximum_marks,
        "marks_scored": marks_scored,
        "improvements": improvements,
        "created_at": datetime.now()
    })

def get_exam_records():
    col = get_collection("exam_records")
    df = pd.DataFrame(list(col.find()))
    if not df.empty and "_id" in df:
        df["_id"] = df["_id"].astype(str)
    return df

def delete_exam_record(record_id):
    col = get_collection("exam_records")
    col.delete_one({"_id": ObjectId(record_id)})

# ---- STUDY PLAN ----

def add_study_plan(plan_date, subject, chapter, planned_hours, remarks):
    col = get_collection("study_plans")
    col.insert_one({
        "plan_date": str(plan_date),
        "subject": subject,
        "chapter": chapter,
        "planned_hours": planned_hours,
        "remarks": remarks,
        "created_at": datetime.now()
    })

def get_study_plans():
    col = get_collection("study_plans")
    df = pd.DataFrame(list(col.find()))
    if not df.empty and "_id" in df:
        df["_id"] = df["_id"].astype(str)
    return df

def delete_study_plan(record_id):
    col = get_collection("study_plans")
    col.delete_one({"_id": ObjectId(record_id)})

# --- Optional: Test connection snippet ---
if __name__ == "__main__":
    try:
        client = get_client()
        client.server_info()  # Verify connection
        print("✅ MongoDB connection successful!")
    except Exception as e:
        print("❌ MongoDB connection failed:", e)

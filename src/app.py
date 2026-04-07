"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional
import os
from pathlib import Path

# Pydantic models for request/response validation
class ActivityCreate(BaseModel):
    """Model for creating a new activity"""
    description: str
    schedule: str
    max_participants: int

class ActivityUpdate(BaseModel):
    """Model for updating an activity"""
    description: Optional[str] = None
    schedule: Optional[str] = None
    max_participants: Optional[int] = None

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"]
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is signed up
    if email not in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Remove student
    activity["participants"].remove(email)
    return {"message": f"Unregistered {email} from {activity_name}"}


# CRUD Operations for Activities

@app.post("/activities")
def create_activity(name: str, activity_data: ActivityCreate):
    """Create a new activity"""
    # Validate activity doesn't already exist
    if name in activities:
        raise HTTPException(
            status_code=400,
            detail=f"Activity '{name}' already exists"
        )
    
    # Validate max_participants is positive
    if activity_data.max_participants <= 0:
        raise HTTPException(
            status_code=400,
            detail="max_participants must be a positive number"
        )
    
    # Create the new activity
    activities[name] = {
        "description": activity_data.description,
        "schedule": activity_data.schedule,
        "max_participants": activity_data.max_participants,
        "participants": []
    }
    
    return {
        "message": f"Activity '{name}' created successfully",
        "activity": {name: activities[name]}
    }


@app.get("/activities/{activity_name}")
def get_activity(activity_name: str):
    """Get details of a specific activity"""
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    return {activity_name: activities[activity_name]}


@app.put("/activities/{activity_name}")
def update_activity(activity_name: str, activity_data: ActivityUpdate):
    """Update an existing activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Get the activity
    activity = activities[activity_name]
    
    # Update fields if provided
    if activity_data.description is not None:
        activity["description"] = activity_data.description
    
    if activity_data.schedule is not None:
        activity["schedule"] = activity_data.schedule
    
    if activity_data.max_participants is not None:
        if activity_data.max_participants <= 0:
            raise HTTPException(
                status_code=400,
                detail="max_participants must be a positive number"
            )
        activity["max_participants"] = activity_data.max_participants
    
    return {
        "message": f"Activity '{activity_name}' updated successfully",
        "activity": {activity_name: activity}
    }


@app.delete("/activities/{activity_name}")
def delete_activity(activity_name: str):
    """Delete an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Delete the activity
    del activities[activity_name]
    
    return {"message": f"Activity '{activity_name}' deleted successfully"}

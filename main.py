from fastapi import FastAPI
from typing import Optional
from supabase import create_client, Client
from pydantic import BaseModel
from datetime import datetime, time
import os
from dotenv import load_dotenv
from datetime import datetime, time, timezone
from fastapi import FastAPI, HTTPException


# Load environment variables
load_dotenv()

# 1. Initialize the FastAPI app
app = FastAPI()


class Field(BaseModel):
    field_id: int
    field_name: str
    opening_time: time
    closing_time: time

class Reservation(BaseModel):
    reservation_id: Optional[int] = None
    field_id: int
    field_name: Optional[str] = None  # add this
    user_id: str
    starting_time: datetime

class User(BaseModel):
    user_id: str
    email: str

# 2. Connect to Supabase
# You will find these two links in your Supabase Dashboard under Project Settings -> API
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 3. Create your first endpoint (a test to see if the server works)
@app.get("/")
def read_root():
    return {"message": "Welcome to the SporTime API!"}

# 4. Create an endpoint to fetch your sports fields
@app.get("/fields", response_model=list[Field])
def get_fields():
    response = supabase.table("fields").select("*").execute()
    return response.data

@app.get("/users", response_model=list[User])
def get_users():
    response = supabase.table("users").select("*").execute()
    return response.data

@app.post("/users", response_model=User)
def create_user(user: User):
    response = supabase.table("users").insert(user.dict()).execute()
    return response.data[0]

@app.delete("/users/{user_id}")
def delete_user(user_id: str):
    supabase.table("reservations").delete().eq("user_id", user_id).execute()
    response = supabase.table("users").delete().eq("user_id", user_id).execute()
    return {"message": "User deleted"}


# 5. Create an endpoint to fetch reservations for a specific field
@app.get("/fields/{field_id}/reservations", response_model=list[Reservation])
def get_field_reservations(field_id: int):
    now = datetime.now(timezone.utc).isoformat()
    response = supabase.table("reservations").select("*").eq("field_id", field_id).gt("starting_time", now).execute()
    return response.data


# 6. endpoint to fetch user reservations
@app.get("/users/{user_id}/reservations", response_model=list[Reservation])
def get_user_reservations(user_id: str):
    now = datetime.now(timezone.utc).isoformat()
    response = supabase.table("reservations")\
        .select("*, fields(field_name)")\
        .eq("user_id", user_id)\
        .gt("starting_time", now)\
        .execute()
    
    # Flatten the nested field_name into the reservation object
    for r in response.data:
        if r.get("fields"):
            r["field_name"] = r["fields"]["field_name"]
        del r["fields"]
    
    return response.data

# 7. Create an endpoint to create a new reservation

@app.post("/reservations", response_model=Reservation)
def create_reservation(reservation: Reservation):
    now = datetime.now(timezone.utc).isoformat()

    count_response = supabase.table("reservations")\
        .select("reservation_id", count="exact")\
        .eq("user_id", reservation.user_id)\
        .gte("starting_time", now)\
        .execute()

    print(f"Active reservations count: {count_response.count}")  # debug

    if count_response.count is not None and count_response.count >= 3:
        raise HTTPException(status_code=400, detail="Reservation limit reached")

    data_to_insert = reservation.dict(exclude_none=True)
    if "starting_time" in data_to_insert:
        data_to_insert["starting_time"] = data_to_insert["starting_time"].isoformat()

    response = supabase.table("reservations").insert(data_to_insert).execute()
    return response.data[0]

# 8. Create an endpoint to delete a reservation
@app.delete("/reservations/{reservation_id}")
def delete_reservation(reservation_id: int):
    response = supabase.table("reservations").delete().eq("reservation_id", reservation_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Reservation not found")

    return {"message": "Reservation deleted", "reservation_id": reservation_id}
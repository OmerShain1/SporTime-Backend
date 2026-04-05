from fastapi import FastAPI
from typing import Optional
from supabase import create_client, Client
from pydantic import BaseModel
from datetime import datetime, time

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
SUPABASE_URL = "https://ahlqaydotuczkfkgmqlu.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFobHFheWRvdHVjemtma2dtcWx1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM4MjY0NzEsImV4cCI6MjA4OTQwMjQ3MX0.WszisAw2nCFHZMcC7fSiAhaxIZrvOH0Uolw75Nu6C4U"

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


# 5. Create an endpoint to fetch reservations for a specific field
@app.get("/fields/{field_id}/reservations", response_model=list[Reservation])
def get_field_reservations(field_id: int):
    response = supabase.table("reservations").select("*").eq("field_id", field_id).execute()
    return response.data

# 6. endpoint to fetch user reservations
@app.get("/users/{user_id}/reservations", response_model=list[Reservation])
def get_user_reservations(user_id: str):
    response = supabase.table("reservations")\
        .select("*, fields(field_name)")\
        .eq("user_id", user_id)\
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
    data_to_insert = reservation.dict(exclude_none=True)
    
    # Convert datetime to ISO string so it can be serialized to JSON
    if "starting_time" in data_to_insert:
        data_to_insert["starting_time"] = data_to_insert["starting_time"].isoformat()
    
    response = supabase.table("reservations").insert(data_to_insert).execute()
    return response.data[0]

# 8. Create an endpoint to delete a reservation
@app.delete("/reservations/{reservation_id}")
def delete_reservation(reservation_id: int):
    response = supabase.table("reservations").delete().eq("reservation_id", reservation_id).execute()
    return response.data[0]
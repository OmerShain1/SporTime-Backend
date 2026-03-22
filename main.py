from fastapi import FastAPI
from supabase import create_client, Client
from pydantic import BaseModel
from datetime import time

# 1. Initialize the FastAPI app
app = FastAPI()

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
@app.get("/fields")
def get_fields():
    # This tells Supabase to grab every row from the 'fields' table
    response = supabase.table("fields").select("*").execute()
    return response.data
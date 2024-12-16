from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
import csv
import os

app = FastAPI()

# Define the CSV file path
CSV_FILE = "users.csv"

# Define the user model
class User(BaseModel):
    username: str
    email: EmailStr
    password: str
    address: str = ""

class LoginData(BaseModel):
    username: str
    password: str

class UpdateData(BaseModel):
    username: str
    address: str
    
# Initialize the CSV file if it doesn't exist
def initialize_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["username", "email", "password", "address"])

initialize_csv()

# Helper function to read all users from the CSV file
def read_users():
    with open(CSV_FILE, mode='r') as file:
        reader = csv.DictReader(file)
        return list(reader)

# Helper function to write users to the CSV file
def write_users(users):
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["username", "email", "password", "address"])
        writer.writeheader()
        writer.writerows(users)

# Set up templates directory
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Create User (Register)
@app.post("/register")
def register_user(user: User):
    users = read_users()
    if any(u["username"] == user.username for u in users):
        raise HTTPException(status_code=400, detail="Username already exists.")
    if any(u["email"] == user.email for u in users):
        raise HTTPException(status_code=400, detail="Email already registered.")
    users.append(user.dict())
    write_users(users)
    return {"message": "User registered successfully."}

# Login User
@app.post("/login")
def login_user(data: LoginData):
    users = read_users()
    for user in users:
        if user["username"] == data.username and user["password"] == data.password:
            return {"message": "Login successful."}
    raise HTTPException(status_code=400, detail="Invalid username or password.")

# Delete User
@app.delete("/delete/{username}")
def delete_user(username: str):
    users = read_users()
    updated_users = [user for user in users if user["username"] != username]
    if len(users) == len(updated_users):
        raise HTTPException(status_code=404, detail="User not found.")
    write_users(updated_users)
    return {"message": "User deleted successfully."}

# Update User Address
@app.post("/update")
def update_user_address(data: UpdateData):
    users = read_users()
    user_found = False
    for user in users:
        if user["username"] == data.username:
            user["address"] = data.address
            user_found = True
            break
    if not user_found:
        raise HTTPException(status_code=404, detail="User not found.")
    write_users(users)
    return {"message": "Address updated successfully."}

# HTML Pages
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/delete", response_class=HTMLResponse)
def delete_page(request: Request):
    return templates.TemplateResponse("delete.html", {"request": request})

@app.get("/update", response_class=HTMLResponse)
def update_page(request: Request):
    return templates.TemplateResponse("update.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

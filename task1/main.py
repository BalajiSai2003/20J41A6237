
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
import requests


app = FastAPI()

class TrainInfo(BaseModel):
    trainName: str
    trainNumber: str
    departureTime: dict
    seatsAvailable: dict
    price: dict
    delayedBy: int

def get_authorization_token():
    company_details = {
    "companyName": "Train Central",
    "clientID": "341dae52-e25c-4e83-860c-865cb34df828",
    "clientSecret": "FOEzIaqCZTwtcFOJ",
    "ownerName": "Rahull",
    "ownerEmail": "rahull@abc.edu",
    "rollNo": "190999"
}

    response = requests.post("http://20.244.56.144/train/auth", json=company_details)
    if response.status_code == 200:
        print( response.json()["access_token"] +  "kokokok")
        return response.json()["access_token"]
    else:
        raise HTTPException(status_code=401, detail="Authorization failed")

def get_train_details(train_number: str, token: str = Depends(get_authorization_token)):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"http://20.244.56.144:80/train/trains/{train_number}", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=404, detail="Train not found")

@app.get("/trains", response_model=list[TrainInfo])
async def get_train_schedules(token: str = Depends(get_authorization_token)):
    headers = {"Authorization": f"Bearer {token}"}
    print(token)
    response = requests.get("http://20.244.56.144/train/trains", headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to fetch train data")
    train_data = response.json()
    current_hour = 15  
    filtered_trains = []
    for train in train_data:
        departure_hour = train["departureTime"]["Hours"]
        departure_minute = train["departureTime"]["Minutes"]
        if (departure_hour >= current_hour and departure_minute >= 30) or (departure_hour > current_hour):
            delayed_by = train["delayedBy"]
            train["departureTime"]["Hours"] += delayed_by  
            filtered_trains.append(train)
    return sorted(
        filtered_trains,
        key=lambda x: (
            x["price"]["sleeper"],
            -x["seatsAvailable"]["sleeper"],
            -x["departureTime"]["Hours"],
            -x["departureTime"]["Minutes"],
        ),
    )

@app.get("/trains/{num}", response_model=list[TrainInfo])
async def get_train(num:str,token: str = Depends(get_authorization_token)):
    headers = {"Authorization": f"Bearer {token}"}
    print(token)
    response = requests.get("http://20.244.56.144/train/trains", headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to fetch train data")
    train_data = response.json()
    # print(train_data)
    l = []
    for train in train_data:
        if train["trainNumber"] == num :
            l.append({
    "trainName": train["trainName"],
    "trainNumber": train["trainNumber"],
    "departureTime": train["departureTime"],
    "seatsAvailable": train["seatsAvailable"],
    "price": train["price"],
    "delayedBy": train["delayedBy"]
  })
    return l
from fastapi import FastAPI

app = FastAPI()

@app.get("/data")
def read_data():
    return {"message": "Yeh mera pehla endpoint hai!"}

@app.get("/status")
def read_status():
    return {"status": "success", "intern": "doing-great"}
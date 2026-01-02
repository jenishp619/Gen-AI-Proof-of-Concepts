# client/main.py
import uvicorn
from server import app
from dotenv import load_dotenv

load_dotenv()   # optional – .env is also loaded in tasks

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
from dotenv import load_dotenv
import uvicorn
import os

uvicorn.run("api.main:app", host="0.0.0.0", port=os.getenv("API_PORT"), reload=True)
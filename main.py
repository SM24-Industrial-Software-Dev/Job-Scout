from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import subprocess
import os

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI"}

@app.get("/streamlit")
async def serve_streamlit():
    # Check if Streamlit is already running
    if not any("streamlit" in p.name() for p in psutil.process_iter()):
        subprocess.Popen(["streamlit", "run", "streamlit_app.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return HTMLResponse(content="<h1>Streamlit app is running</h1>", status_code=200)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi import FastAPI, HTTPException
import threading
from Master import Master
from Tables import Notifs

app = FastAPI()
master = Master(18)

# Start the master scheduler in the background
master_thread = threading.Thread(target=master.run, daemon=True)
master_thread.start()

@app.post("/add_job_search/")
def add_job_search(job_search: Notifs):
    try:
        task_id = master.add_task(job_search)
        return {"task_id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

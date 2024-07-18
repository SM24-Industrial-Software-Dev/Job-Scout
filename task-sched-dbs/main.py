from fastapi import FastAPI, HTTPException
import threading
import uvicorn
import os
from Master import Master
from Tables import Notifs, Task
from pydantic import BaseModel

app = FastAPI()
master = Master(18)

# Start the master scheduler in the background
master_thread = threading.Thread(target=master.run, daemon=True)
master_thread.start()

class TaskUpdateRequest(BaseModel):
    task_id: int
    new_task: Task

@app.delete("/delete_task/{task_id}")
def delete_task(task_id: int):
    result = master.delete_task(task_id)
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result

# @app.put("/update_task/{task_id}")
# def update_task(task_id: int, new_task: Task):
#     try: 
#         task = new_task.dict()
#         if master.get_task(task_id).type == 'notif':
#             result = master.update_task(task_id, task)
#             if result["status"] == "error":
#                 raise HTTPException(status_code=500, detail=result["message"])
#             return result
#     except Exception as e: 
#         raise Exception(f"failed to update task with id {task_id}: {e}")


@app.post("/add_search/")
def add_job_search(job_search: Notifs):
    try:
        task_id = master.add_task(job_search)
        return {"task_id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

def run_fastapi():
    uvicorn.run(app, host="0.0.0.0", port=8000)

def run_streamlit():
    os.system('streamlit run ../app_experiment.py')

if __name__ == "__main__":
    fastapi_thread = threading.Thread(target=run_fastapi)
    streamlit_thread = threading.Thread(target=run_streamlit)

    fastapi_thread.start()
    streamlit_thread.start()

    fastapi_thread.join()
    streamlit_thread.join()
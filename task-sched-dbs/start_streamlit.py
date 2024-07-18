import subprocess

def run_streamlit():
    subprocess.run(["streamlit", "run", "app_experiment.py"])  # Ensure "streamlit_app.py" is the name of your Streamlit script

if __name__ == "__main__":
    run_streamlit()

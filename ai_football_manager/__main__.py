import subprocess

try:
    subprocess.run(["streamlit", "run", "ai_football_manager/app.py"])
except KeyboardInterrupt:
    pass
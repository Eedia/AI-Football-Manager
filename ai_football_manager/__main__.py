import subprocess

try:
    subprocess.run(["streamlit", "run", "ai_football_manager/app.py","--logger.level=error"])
except KeyboardInterrupt:
    pass
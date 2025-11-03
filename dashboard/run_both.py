import subprocess
import sys

# Start both servers
uvicorn = subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app", "--port", "8000"])
streamlit = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "dashboard/app.py", "--server.port", "8501"])

try:
    uvicorn.wait()
    streamlit.wait()
except KeyboardInterrupt:
    uvicorn.terminate()
    streamlit.terminate()

"""
Run CIMR Claims Automation UI
"""
import subprocess
import sys

if __name__ == "__main__":
    # Run Streamlit app
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])

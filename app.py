# app.py - Render Entry Point
import os
import sys

# Force Streamlit to use frontend.py
if __name__ == "__main__":
    os.system("streamlit run frontend.py --server.port $PORT --server.address 0.0.0.0")
    sys.exit(0)

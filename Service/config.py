from dotenv import load_dotenv
import os

load_dotenv()

DB_FILE = os.environ.get('DB_FILE', 'data.db')
UI_EXE_PATH = os.environ.get('UI_EXE_PATH', 'BTread-UI.exe')
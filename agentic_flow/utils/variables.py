import os

MAIN_DIR = os.path.dirname(os.path.dirname(__file__))
LOG_FOLDER = os.path.join(MAIN_DIR,'logs')

from dotenv import load_dotenv
load_dotenv(os.path.join(MAIN_DIR, '.env'), override=True)




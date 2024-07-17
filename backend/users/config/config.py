import os

from dotenv import load_dotenv


env = os.environ.get
load_dotenv('./.env')

ALLOWED_ORIGINS = env('ALLOWED_ORIGINS').split(',')
LOG_FILE_PATH = env('LOG_FILE_PATH')

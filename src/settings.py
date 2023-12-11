from dotenv import load_dotenv
import pathlib


load_dotenv(verbose=True)
ROOT = pathlib.Path(__file__).parent
DATA_DIR = ROOT / 'data'

PROXY = 'http://127.0.0.1:7890'
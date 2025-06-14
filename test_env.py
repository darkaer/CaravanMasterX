from dotenv import load_dotenv
import os

load_dotenv()
print("DUNE_API_KEY:", os.getenv("DUNE_API_KEY")) 
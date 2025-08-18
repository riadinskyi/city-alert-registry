import os
from dotenv import load_dotenv


load_dotenv()

air_alert_api_token = os.getenv("AIR_ALERT_API_TOKEN")
correct_token = os.getenv("CORRECT_TOKEN")
print()

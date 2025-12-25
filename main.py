from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

SERPAPI_KEY = os.getenv("SERPAPI_KEY")
SERPAPI_URL = "https://serpapi.com/search"

def search_jobs(query):
    params = {
        "engine": "google_jobs",
        "q": query,
        "api_key": SERPAPI_KEY
    }

    r = requests.get(SERPAPI_URL, params=params)
    data = r.json()

    # If no jobs found
    if "jobs_results" not in data:
        return []

    results = []
    for job in data["jobs_results"]:
        title = job.get("title", "No title")
        company = job.get("company_name", "Unknown company")
        location = job.get("location", "Unknown location")
        link = job.get("link") or job.get("job_link") or job.get("apply_link") or "No link available"



        formatted = f"{title}\n{company} — {location}\nApply: {link}"
        results.append(formatted)

    return results


@app.route("/", methods=["POST"])
def bot():
    user_msg = request.values.get("Body", "").strip()
    response = MessagingResponse()

    query = f"{user_msg} jobs"
    results = search_jobs(query)

    msg = response.message(f"🔎 Job results for: '{user_msg}'")

    if not results:
        msg.body("No job listings found.")
        return str(response)

    # Format results for WhatsApp
    body_text = "\n\n".join(results)
    msg.body(body_text)

    return str(response)


if __name__ == "__main__":
    app.run()
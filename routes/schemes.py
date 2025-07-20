import requests
from flask import Blueprint, render_template

schemes_bp = Blueprint('schemes', __name__)

@schemes_bp.route('/schemes')
def farmer_schemes():
    url = "https://api.data.gov.in/resource/447621c5-d0d6-42c8-820d-7cbb3354ad1b"
    params = {
        "api-key": "579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b",
        "format": "json"
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        schemes = data.get("records", [])
        return render_template("schemes.html", schemes=schemes)
    except Exception as e:
        return f"Failed to fetch schemes: {str(e)}"

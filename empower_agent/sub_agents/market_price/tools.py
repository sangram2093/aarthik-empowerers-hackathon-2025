import requests
from datetime import datetime
from datetime import timedelta
def get_current_market_price(crop_name: str, state: str, district: str, api: str) -> str:
    api_url = "https://api.data.gov.in/resource/35985678-0d79-46b4-9ed6-6f13308a1d24"
    api_key = "579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b"
    limit = 10  # Number of records per page
    offset = 0  # Start offset for pagination
    all_records = []
    arrival_date = (datetime.now() - timedelta(days=1)).strftime("%d/%m/%Y")
    crop_records = []
    try:
        while True:
            # Update parameters for the current page
            params = {
                "api-key": api_key,
                "format": "json",
                "limit": limit,
                "offset": offset,
                "filters[State]": state,
                "filters[District]": district,
                "filters[Arrival_Date]": arrival_date,
            }

            headers = {"accept": "application/xml"}

            # Make the API request
            response = requests.get(api_url, params=params, headers=headers)
            response.raise_for_status()  # Raise an error for HTTP issues
            data = response.json()

            # Extract records from the response
            records = data.get("records", [])
            if not records:  # Break the loop if no more records are returned
                break
            all_records.extend(records)

            # Update the offset for the next page
            offset += limit

        # Process all_records to extract prices or other required data
        for record in all_records:
            if crop_name.lower() in record.get('Commodity', '').lower():
                crop_records.append(record)
        
        return crop_records if crop_records else f"{crop_name} has not been traded for the current date. Historcal data would be helpful to get some idea on the price"

    except Exception as e:
        return f"Error fetching market price: {e}"

def get_schemes_info():
    """
    Fetches information about government schemes like PM-Kisan.
    This could involve scraping, using official APIs (if available),
    or retrieving from a pre-defined database/JSON file.
    """
    print("Fetching government schemes information...")
    # Mock Data for demonstration
    schemes_data = [
        {
            "name": "PM-Kisan Samman Nidhi Yojana",
            "description": "Provides income support to all eligible farmer families across the country.",
            "eligibility": "Landholding farmers families with cultivable land.",
            "benefits": "₹6000 per year in three equal installments of ₹2000.",
            "link": "https://pmkisan.gov.in/"
        },
        {
            "name": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
            "description": "Provides comprehensive insurance cover against failure of crops.",
            "eligibility": "All farmers growing notified crops in notified areas.",
            "benefits": "Financial support to farmers suffering crop loss/damage arising out of unforeseen events.",
            "link": "https://pmfby.gov.in/"
        },
        {
            "name": "Kisan Credit Card (KCC) Scheme",
            "description": "Provides adequate and timely credit support from the banking system to the farmers.",
            "eligibility": "Farmers - individual/joint cultivators, tenant farmers, SHGs, JLGs.",
            "benefits": "Flexible and simplified procedure for credit access for agriculture and allied activities.",
            "link": "https://www.nabard.org/content.aspx?id=516"
        }
    ]
    return schemes_data

if __name__ == '__main__':
    schemes = get_schemes_info()
    print("Government Schemes:", schemes)
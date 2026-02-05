import re

def extract_intelligence(text: str):
    return {
        "upi_ids": re.findall(r'[\w.-]+@[\w]+', text),
        "bank_accounts": re.findall(r'\b\d{9,18}\b', text),
        "phishing_urls": re.findall(r'https?://\S+', text)
    }

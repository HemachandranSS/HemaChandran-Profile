import requests

url = "https://hrce.tn.gov.in/hrcehome/dashboarddetails.php"

params = {
    "tid": "1"
}

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(
    url,
    params=params,
    headers=headers,
    timeout=30
)

print("Status:", response.status_code)
print(response.url)

# Save the complete HR&CE HTML
with open("hrce_temple.html", "w", encoding="utf-8") as f:
    f.write(response.text)

print("Saved HR&CE page")


hrce.tn.gov.in/hrcehome/index_temple.php?tid=1
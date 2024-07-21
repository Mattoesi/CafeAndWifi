import requests

# Define the URL and the headers
url = "http://127.0.0.1:5000/add"
headers = {
    "api-key": "SecretKey"
}

# Define the data to be sent in the POST request
data = {
    "name": "Test Cafe",
    "map_url": "http://example.com",
    "img_url": "http://example.com/img.jpg",
    "loc": "Test Location",
    "seats": "20",
    "toilet": "true",
    "wifi": "true",
    "sockets": "true",
    "calls": "true",
    "coffee_price": "$4"
}

# Send the POST request
response = requests.post(url, headers=headers, data=data)

# Print the response
print(response.json())

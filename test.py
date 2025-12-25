# -*- coding: utf-8 -*-
import requests
import json

API_URL = "http://localhost:5000/api"

# Test 1: Health
resp = requests.get(f"{API_URL}/health")
print("Health:", resp.json())

# Test 2: GET clientes
resp = requests.get(f"{API_URL}/clientes")
print("Clientes (vacío):", resp.json())

# Test 3: POST cliente
data = {
    "nombre": "Juan Pérez",
    "telefono": "1123456789",
    "email": "juan@test.com"
}
resp = requests.post(f"{API_URL}/clientes", json=data)
print("POST Status:", resp.status_code)
print("POST Response:", resp.json())

# Test 4: GET clientes again
resp = requests.get(f"{API_URL}/clientes")
print("Clientes después:", resp.json())
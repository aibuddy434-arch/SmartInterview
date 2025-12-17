#!/usr/bin/env python3
import asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Create a minimal FastAPI app for testing
app = FastAPI()

@app.get("/test")
async def test():
    return {"message": "test"}

# Test with TestClient
client = TestClient(app)
response = client.get("/test")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

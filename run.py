"""
Entry point to run the Mock Admin Dashboard.
Usage: python run.py
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)

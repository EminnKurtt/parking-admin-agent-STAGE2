from fastapi import FastAPI, HTTPException, Header
from app.schemas import ReservationRequest, StatusResponse
from core.config import settings

app = FastAPI(
    title="Mock Admin Dashboard API",
    description="Simulates a human administrator reviewing reservation requests.",
    version="1.0.0"
)

# In-memory database (resets when server restarts)
admin_requests: dict = {}

ADMIN_API_KEY = settings.ADMIN_API_KEY


@app.get("/")
def read_root():
    """Health check endpoint."""
    return {
        "message": "Mock Admin Dashboard API is running.",
        "endpoints": {
            "create_request": "POST /admin/requests",
            "approve_request": "POST /admin/approve/{request_id}",
            "check_status": "GET /admin/status/{request_id}",
            "list_all": "GET /admin/requests"
        }
    }


@app.post("/admin/requests")
def create_reservation_request(request: ReservationRequest, x_api_key: str = Header(...)):
    """Receives a new reservation request from the Admin Agent."""
    if x_api_key != ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")

    if request.request_id in admin_requests:
        raise HTTPException(status_code=409, detail="Request ID already exists")

    admin_requests[request.request_id] = request

    print(f"\n{'='*60}")
    print("NEW RESERVATION REQUEST RECEIVED")
    print(f"{'='*60}")
    print(f"Request ID: {request.request_id}")
    print(f"User: {request.user_name}")
    print(f"Car: {request.car_number}")
    print(f"Period: {request.reservation_period}")
    print(f"Message from Agent:\n{request.formatted_message}")
    print(f"{'='*60}\n")

    return {"status": "received", "request_id": request.request_id}


@app.post("/admin/approve/{request_id}")
def approve_or_reject(
    request_id: str,
    action: str = "APPROVED",
    x_api_key: str = Header(...)
):
    """Simulates the admin approving or rejecting a request."""
    if x_api_key != ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")

    if action not in ["APPROVED", "REJECTED"]:
        raise HTTPException(status_code=400, detail="Action must be APPROVED or REJECTED")

    if request_id not in admin_requests:
        raise HTTPException(status_code=404, detail="Request not found")

    admin_requests[request_id].status = action
    print(f"[Admin Dashboard] Request {request_id} has been {action}.")

    return {"status": "success", "new_status": action}


@app.get("/admin/status/{request_id}", response_model=StatusResponse)
def check_status(request_id: str, x_api_key: str = Header(...)):
    """Returns the current status of a reservation request."""
    if x_api_key != ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")

    if request_id not in admin_requests:
        raise HTTPException(status_code=404, detail="Request not found")

    return StatusResponse(
        request_id=request_id,
        status=admin_requests[request_id].status
    )


@app.get("/admin/requests")
def list_all_requests(x_api_key: str = Header(...)):
    """Debug endpoint: lists all requests (requires API key)."""
    if x_api_key != ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")
    return {"total": len(admin_requests), "requests": list(admin_requests.values())}

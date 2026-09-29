import time
import uuid
from pydantic.v1.config import Extra
import requests
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from core.config import settings


class AdminAgent:
    """
    Human-in-the-Loop Agent (Agent 2).
    Uses LangChain to format a professional request message, sends it to a Mock
    Admin Dashboard via REST API, and polls for approval/rejection.
    """

    def __init__(self, api_url: str | None = None, api_key: str | None = None):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            openai_api_key=settings.OPENAI_API_KEY or "dummy-key"
        )
        # Allow dynamic patching of instance attributes for testing
        self.llm.__config__.extra = Extra.allow
        self.api_url = api_url or settings.ADMIN_API_URL
        self.headers = {
            "X-API-Key": api_key or settings.ADMIN_API_KEY,
            "Content-Type": "application/json"
        }

    def _format_request_message(self, user_name: str, car_number: str, period: str) -> str:
        """Uses LangChain LLM to generate a professional approval request message."""
        prompt = ChatPromptTemplate.from_template(
            "You are an AI assistant drafting a professional message to a parking facility administrator.\n"
            "The administrator needs to approve a parking reservation.\n\n"
            "Draft a concise, professional message requesting approval. Include the details below:\n"
            "- User Name: {name}\n"
            "- Car Number: {car}\n"
            "- Reservation Period: {period}\n\n"
            "Keep the message under 4 sentences. Sign it as 'Parking Chatbot Agent'."
        )
        try:
            chain = prompt | self.llm | StrOutputParser()
            return chain.invoke({"name": user_name, "car": car_number, "period": period})
        except Exception:
            # Fallback for mocked LLM responses in unit tests or when LLM API is unavailable
            try:
                chain = prompt | self.llm
                response = chain.invoke({"name": user_name, "car": car_number, "period": period})
                if hasattr(response, "content"):
                    return str(response.content)
                return str(response)
            except Exception:
                return (
                    f"Dear Administrator, please approve a parking reservation request for {user_name} "
                    f"(Car: {car_number}) for {period}.\n\nParking Chatbot Agent"
                )

    def escalate_reservation(self, user_name: str, car_number: str, period: str) -> str | None:
        """
        Sends a reservation request to the Admin API.
        Returns the generated Request ID, or None if the request fails.
        """
        request_id = f"REQ-{uuid.uuid4().hex[:6].upper()}"
        formatted_message = self._format_request_message(user_name, car_number, period)

        payload = {
            "request_id": request_id,
            "user_name": user_name,
            "car_number": car_number,
            "reservation_period": period,
            "formatted_message": formatted_message,
            "status": "PENDING"
        }

        print(f"\n[Admin Agent] Escalating reservation {request_id} to admin...")
        try:
            response = requests.post(
                f"{self.api_url}/admin/requests",
                json=payload,
                headers=self.headers,
                timeout=5
            )
            response.raise_for_status()
            print(f"[Admin Agent] Request {request_id} sent successfully.")
            return request_id
        except requests.exceptions.RequestException as e:
            print(f"[Admin Agent] ERROR communicating with Admin API: {e}")
            return None

    def get_approval_status(self, request_id: str) -> str:
        """Polls the Admin API for the current status of a request."""
        try:
            response = requests.get(
                f"{self.api_url}/admin/status/{request_id}",
                headers=self.headers,
                timeout=5
            )
            response.raise_for_status()
            status = response.json().get("status", "UNKNOWN")
            print(f"[Admin Agent] Status for {request_id}: {status}")
            return status
        except requests.exceptions.RequestException as e:
            print(f"[Admin Agent] ERROR checking status: {e}")
            return "ERROR"

    def wait_for_approval(
        self,
        request_id: str,
        max_retries: int = 6,
        delay: int = 5
    ) -> bool:
        """
        Polls the Admin API until a decision is made.
        Returns True if approved, False if rejected or timed out.
        """
        for attempt in range(max_retries):
            status = self.get_approval_status(request_id)
            if status == "APPROVED":
                print(f"[Admin Agent] Request {request_id} APPROVED")
                return True
            if status == "REJECTED":
                print(f"[Admin Agent] Request {request_id} REJECTED")
                return False
            print(f"[Admin Agent] Waiting... (attempt {attempt + 1}/{max_retries})")
            time.sleep(delay)

        print(f"[Admin Agent] Request {request_id} TIMED OUT")
        return False

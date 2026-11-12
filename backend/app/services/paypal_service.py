"""PayPal Orders API v2 Sandbox Integration Service.

SECURITY & VERIFICATION:
- Integrates with PayPal REST API v2 Sandbox endpoints.
- Server-side order creation and capture validation.
- Secure server-side webhook signature verification via PayPal API.
- OAuth2 token caching with expiration threshold.
- Decimal precision for monetary amounts (no float errors).
- Automatic fallback to MockPayPalOrderService when credentials are not configured.
"""

import json
import logging
import time
from decimal import Decimal
from typing import Any, Dict, Optional
import httpx

from app.core.config import settings
from app.core.exceptions import PaymentException, PaymentVerificationException
from app.services.payment_service import IPayPalOrderService, MockPayPalOrderService
from app.utils.currency import normalize_currency, to_decimal_amount

logger = logging.getLogger("flowforge.services.paypal")


class PayPalSandboxService(IPayPalOrderService):
    """Production-grade client for PayPal Orders API v2 Sandbox."""

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        base_url: Optional[str] = None,
        webhook_id: Optional[str] = None,
        http_client: Optional[httpx.Client] = None,
    ):
        self.client_id = client_id or settings.PAYPAL_CLIENT_ID or ""
        self.client_secret = client_secret or settings.PAYPAL_CLIENT_SECRET or ""
        self.base_url = (base_url or settings.PAYPAL_BASE_URL or "https://api-m.sandbox.paypal.com").rstrip("/")
        self.webhook_id = webhook_id or settings.PAYPAL_WEBHOOK_ID or ""
        self._http_client = http_client
        self._token_cache: Optional[Dict[str, Any]] = None

    def _get_client(self) -> httpx.Client:
        if self._http_client is not None:
            return self._http_client
        return httpx.Client(timeout=30.0)

    def get_access_token(self) -> str:
        """Obtain or reuse cached OAuth2 Bearer token from PayPal."""
        now = time.time()
        if self._token_cache and self._token_cache.get("expires_at", 0) > now + 60:
            return self._token_cache["access_token"]

        if not self.client_id or not self.client_secret:
            raise PaymentException("PayPal Client ID or Secret is not configured.")

        url = f"{self.base_url}/v1/oauth2/token"
        headers = {"Accept": "application/json", "Accept-Language": "en_US"}
        data = {"grant_type": "client_credentials"}

        try:
            client = self._get_client()
            response = client.post(
                url,
                headers=headers,
                data=data,
                auth=(self.client_id, self.client_secret),
            )
            response.raise_for_status()
            token_data = response.json()
            access_token = token_data.get("access_token")
            expires_in = int(token_data.get("expires_in", 3600))

            if not access_token:
                raise PaymentException("Failed to extract access_token from PayPal response")

            self._token_cache = {
                "access_token": access_token,
                "expires_at": now + expires_in,
            }
            logger.debug("Successfully refreshed PayPal OAuth2 token (expires in %ds)", expires_in)
            return access_token
        except httpx.HTTPStatusError as e:
            logger.error("PayPal OAuth2 token request failed: %s - %s", e.response.status_code, e.response.text)
            raise PaymentException(f"PayPal authentication failed: HTTP {e.response.status_code}") from e
        except Exception as e:
            logger.error("PayPal token error: %s", str(e))
            raise PaymentException(f"Unable to reach PayPal API: {str(e)}") from e

    def create_order(
        self,
        amount: Decimal,
        currency: str,
        reference_id: str,
        description: Optional[str] = None,
        return_url: Optional[str] = None,
        cancel_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create an authorized order in PayPal Sandbox."""
        token = self.get_access_token()
        normalized_curr = normalize_currency(currency)
        dec_amount = to_decimal_amount(amount)

        url = f"{self.base_url}/v2/checkout/orders"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

        order_payload: Dict[str, Any] = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "reference_id": reference_id,
                    "description": description or f"FlowForge AI Payment {reference_id}",
                    "custom_id": reference_id,
                    "amount": {
                        "currency_code": normalized_curr,
                        "value": f"{dec_amount:.2f}",
                    },
                }
            ],
        }

        if return_url and cancel_url:
            order_payload["payment_source"] = {
                "paypal": {
                    "experience_context": {
                        "payment_method_preference": "IMMEDIATE_PAYMENT_REQUIRED",
                        "brand_name": "FlowForge AI",
                        "locale": "en-US",
                        "user_action": "PAY_NOW",
                        "return_url": return_url,
                        "cancel_url": cancel_url,
                    }
                }
            }

        try:
            client = self._get_client()
            resp = client.post(url, headers=headers, json=order_payload)
            resp.raise_for_status()
            data = resp.json()

            order_id = data.get("id")
            status = data.get("status", "CREATED")

            # Extract approval link
            approve_url = None
            for link in data.get("links", []):
                if link.get("rel") in ("approve", "payer-action"):
                    approve_url = link.get("href")
                    break

            logger.info("PayPal order created: %s (status=%s)", order_id, status)
            return {
                "id": order_id,
                "status": status,
                "amount": f"{dec_amount:.2f}",
                "currency": normalized_curr,
                "approve_url": approve_url,
                "raw": data,
            }
        except httpx.HTTPStatusError as e:
            logger.error("PayPal order creation failed: %s - %s", e.response.status_code, e.response.text)
            raise PaymentException(f"Failed to create PayPal order: {e.response.text}") from e
        except Exception as e:
            logger.error("PayPal order error: %s", str(e))
            raise PaymentException(f"PayPal order creation encountered an error: {str(e)}") from e

    def capture_order(self, paypal_order_id: str) -> Dict[str, Any]:
        """Capture an approved PayPal order server-side."""
        token = self.get_access_token()
        url = f"{self.base_url}/v2/checkout/orders/{paypal_order_id}/capture"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

        try:
            client = self._get_client()
            resp = client.post(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()

            status = data.get("status")
            if status != "COMPLETED":
                raise PaymentVerificationException(
                    f"PayPal order capture did not complete successfully. Status: {status}",
                    details={"order_id": paypal_order_id, "paypal_response": data},
                )

            # Extract capture ID and captured amount
            captures = (
                data.get("purchase_units", [{}])[0]
                .get("payments", {})
                .get("captures", [])
            )
            capture_id = captures[0].get("id") if captures else None
            amount_captured = captures[0].get("amount", {}).get("value") if captures else None

            logger.info("PayPal order [%s] captured successfully: capture_id=%s", paypal_order_id, capture_id)
            return {
                "id": capture_id or paypal_order_id,
                "order_id": paypal_order_id,
                "capture_id": capture_id,
                "status": "COMPLETED",
                "amount_captured": amount_captured,
                "raw": data,
            }
        except httpx.HTTPStatusError as e:
            logger.error("PayPal capture failed: %s - %s", e.response.status_code, e.response.text)
            raise PaymentVerificationException(
                f"PayPal order capture failed: {e.response.text}",
                details={"order_id": paypal_order_id, "status_code": e.response.status_code},
            ) from e
        except PaymentVerificationException:
            raise
        except Exception as e:
            logger.error("PayPal capture error: %s", str(e))
            raise PaymentVerificationException(f"Error capturing PayPal order: {str(e)}") from e

    def get_order_status(self, paypal_order_id: str) -> Dict[str, Any]:
        """Authoritatively query PayPal server for order status."""
        token = self.get_access_token()
        url = f"{self.base_url}/v2/checkout/orders/{paypal_order_id}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

        try:
            client = self._get_client()
            resp = client.get(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()

            return {
                "id": data.get("id"),
                "status": data.get("status"),
                "raw": data,
            }
        except httpx.HTTPStatusError as e:
            logger.error("PayPal get_order_status failed: %s - %s", e.response.status_code, e.response.text)
            raise PaymentException(f"Failed to fetch PayPal order status: {e.response.text}") from e
        except Exception as e:
            raise PaymentException(f"Error querying PayPal order status: {str(e)}") from e

    def verify_webhook_signature(
        self,
        headers: Dict[str, str],
        body_bytes: bytes,
    ) -> bool:
        """Verify the authenticity of an incoming PayPal Webhook via PayPal API.

        Uses PayPal's /v1/notifications/verify-webhook-signature endpoint.
        """
        if not self.webhook_id:
            logger.warning("PAYPAL_WEBHOOK_ID not configured; webhook verification cannot proceed.")
            return False

        token = self.get_access_token()
        url = f"{self.base_url}/v1/notifications/verify-webhook-signature"
        http_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

        # Case-insensitive header lookup
        def _get_h(k: str) -> Optional[str]:
            k_lower = k.lower()
            for key, val in headers.items():
                if key.lower() == k_lower:
                    return val
            return None

        auth_algo = _get_h("paypal-auth-algo")
        cert_url = _get_h("paypal-cert-url")
        transmission_id = _get_h("paypal-transmission-id")
        transmission_sig = _get_h("paypal-transmission-sig")
        transmission_time = _get_h("paypal-transmission-time")

        if not all([auth_algo, cert_url, transmission_id, transmission_sig, transmission_time]):
            logger.warning("Missing required PayPal webhook signature headers")
            return False

        try:
            body_json = json.loads(body_bytes.decode("utf-8"))
        except Exception as e:
            logger.warning("Could not decode webhook body as JSON: %s", e)
            return False

        verify_payload = {
            "auth_algo": auth_algo,
            "cert_url": cert_url,
            "transmission_id": transmission_id,
            "transmission_sig": transmission_sig,
            "transmission_time": transmission_time,
            "webhook_id": self.webhook_id,
            "webhook_event": body_json,
        }

        try:
            client = self._get_client()
            resp = client.post(url, headers=http_headers, json=verify_payload)
            resp.raise_for_status()
            res_data = resp.json()
            is_valid = res_data.get("verification_status") == "SUCCESS"
            logger.info("PayPal webhook verification outcome: %s", res_data.get("verification_status"))
            return is_valid
        except Exception as e:
            logger.error("PayPal webhook signature verification failed with error: %s", e)
            return False


def get_paypal_service() -> IPayPalOrderService:
    """Return configured PayPal client or fallback Mock provider."""
    client_id = (settings.PAYPAL_CLIENT_ID or "").strip()
    secret = (settings.PAYPAL_CLIENT_SECRET or "").strip()
    is_placeholder = "placeholder" in client_id.lower() or "placeholder" in secret.lower()

    if not client_id or not secret or is_placeholder:
        logger.info("PayPal credentials not set or placeholder detected — using MockPayPalOrderService")
        return MockPayPalOrderService()

    return PayPalSandboxService()


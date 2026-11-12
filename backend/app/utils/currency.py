"""High-precision financial arithmetic and currency utilities for FlowForge AI.

STRICT FINANCIAL RULES:
1. Always use Python `Decimal` for all monetary amounts.
2. NEVER use floating-point math for pricing, fee calculations, or revenue aggregation.
3. Supported currencies: USD, EUR, INR.
4. Currencies must be tracked and aggregated separately; never mix currencies into a single sum.
"""

from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from typing import Dict, Set, Union
from pydantic import BaseModel, Field

SUPPORTED_CURRENCIES: Set[str] = {"USD", "EUR", "INR"}

CURRENCY_SYMBOLS: Dict[str, str] = {
    "USD": "$",
    "EUR": "€",
    "INR": "₹",
}

# Standard 2-decimal-place monetary quantizer
CENT_QUANTIZER = Decimal("0.01")


def normalize_currency(currency_code: str) -> str:
    """Normalize and validate a currency code.
    
    Returns uppercase currency string.
    Raises ValueError if currency is unsupported.
    """
    if not currency_code or not isinstance(currency_code, str):
        raise ValueError("Currency code must be a non-empty string.")

    cleaned = currency_code.strip().upper()
    if cleaned not in SUPPORTED_CURRENCIES:
        raise ValueError(
            f"Unsupported currency: '{currency_code}'. Supported currencies are: {sorted(list(SUPPORTED_CURRENCIES))}"
        )
    return cleaned


def to_decimal_amount(value: Union[str, int, float, Decimal]) -> Decimal:
    """Safely convert any numeric value to a 2-decimal-place quantized Decimal.
    
    Avoids binary floating-point representation bugs by converting floats to strings first.
    """
    if value is None:
        raise ValueError("Amount cannot be None.")

    try:
        if isinstance(value, float):
            d = Decimal(str(value))
        elif isinstance(value, (str, int, Decimal)):
            d = Decimal(str(value).strip())
        else:
            raise ValueError(f"Unsupported type for monetary conversion: {type(value)}")

        return d.quantize(CENT_QUANTIZER, rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"Invalid monetary format '{value}': {str(exc)}") from exc


def format_currency_display(amount: Union[Decimal, float, int, str], currency_code: str = "USD") -> str:
    """Format an amount with its currency symbol and 2 decimal places."""
    normalized_curr = normalize_currency(currency_code)
    dec_amount = to_decimal_amount(amount)
    symbol = CURRENCY_SYMBOLS.get(normalized_curr, normalized_curr)
    return f"{symbol}{dec_amount:,.2f}"


class CurrencyRevenueBreakdown(BaseModel):
    """Container for segregated revenues across supported currencies.
    
    Strictly keeps currencies isolated to prevent invalid currency mixing.
    """
    total_usd: Decimal = Field(default=Decimal("0.00"), description="Total revenue in USD")
    total_inr: Decimal = Field(default=Decimal("0.00"), description="Total revenue in INR")
    total_eur: Decimal = Field(default=Decimal("0.00"), description="Total revenue in EUR")

    def add(self, amount: Union[Decimal, float, int, str], currency: str) -> None:
        """Add an amount to the corresponding currency bucket."""
        curr = normalize_currency(currency)
        dec_amount = to_decimal_amount(amount)
        if curr == "USD":
            self.total_usd = (self.total_usd + dec_amount).quantize(CENT_QUANTIZER)
        elif curr == "INR":
            self.total_inr = (self.total_inr + dec_amount).quantize(CENT_QUANTIZER)
        elif curr == "EUR":
            self.total_eur = (self.total_eur + dec_amount).quantize(CENT_QUANTIZER)

    def to_dict(self) -> Dict[str, float]:
        """Convert to JSON-serializable float values for frontend compatibility."""
        return {
            "totalRevenueUsd": float(self.total_usd),
            "totalRevenueInr": float(self.total_inr),
            "totalRevenueEur": float(self.total_eur),
        }


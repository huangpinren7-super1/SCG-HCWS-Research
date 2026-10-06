from __future__ import annotations

from typing import Final

API_SCHEMA: Final = 'scg-hcws-bootloops-api-v1'
RECEIPT_SCHEMA: Final = 'scg-hcws-bootloops-receipt-v1'
OPERATIONS: Final = ('catalog', 'guide', 'acceptance')


def validate_operation(operation: str) -> None:
    if operation not in OPERATIONS:
        raise ValueError(f'Unsupported operation: {operation}')
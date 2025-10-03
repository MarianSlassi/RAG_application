from fastapi import status
from typing import Dict, Any
from src.qabot.api.schemas import AskResponse

ask_responses: Dict[int | str, Dict[str, Any]]  = {
    status.HTTP_200_OK: {
        "description": "Successful response with LLM answer and sources",
        "model": AskResponse,
        "content": {
            "application/json": {
                "example": {
                    "answer": "To reinstall a printer, follow these steps:\n\n1. First, locate the printer's IP address...",
                    "sources": [
                        {
                            "title": "009_resetting-a-jammed-printer",
                            "path": "/data/01_raw/it-knowledge/canonical/md/009_resetting-a-jammed-printer.mdf",
                            "updated_at": "2025-08-26"
                        }
                    ],
                    "timing": {
                        "retrieve_ms": 128,
                        "llm_ms": 7355,
                        "total_ms": 7483
                    }
                }
            }
        }
    },
    status.HTTP_400_BAD_REQUEST: {
        "description": "Bad request (e.g., empty question)"
    },
    status.HTTP_422_UNPROCESSABLE_ENTITY: {
        "description": "Validation error in input data"
    },
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "description": "Internal server error"
    },
    status.HTTP_503_SERVICE_UNAVAILABLE: {
        "description": "Service temporarily unavailable (e.g., LLM or retriever down)"
    }
}
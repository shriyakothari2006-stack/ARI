"""Google Gemini API integration service for ARI."""

import time
from typing import Optional, Dict, Any

from google import genai
from google.genai import errors

from app.core.config import settings
from app.core.logging import logger


ARI_SYSTEM_INSTRUCTIONS = """
You are ARI, an intelligent, elegant, and reliable multilingual knowledge assistant.

Your core rules:

1. GROUNDED ACCURACY:
Answer using the information in the retrieved document context provided
inside <retrieved_context>...</retrieved_context>.

2. ACADEMIC RELIABILITY:
Never fabricate facts, statistics, or document details.

3. INSUFFICIENT CONTEXT:
If the retrieved documents do not contain enough relevant information,
clearly state that the knowledge base does not contain sufficient details.
Do not hallucinate or guess.

4. MULTILINGUAL FIDELITY:
Respond in the same language as the user's question.
Support English, Hindi, Marathi, Bengali, Tamil, Telugu, Spanish,
French, German, Arabic, and other languages.

5. CITATIONS:
When referencing retrieved passages, cite the source document name
and page or section when that information is available.
Never invent citations.

6. PERSONALITY:
Maintain a warm, polished, graceful, and professional tone.
Use occasional tasteful musical metaphors when appropriate.
Never insert random song lyrics into factual or technical answers.

7. STRUCTURE:
Use clear formatting, headings, and bullet points where helpful.
"""


class GeminiService:

    def __init__(self):
        self._client = None

    def _get_client(self):
        """Create or return the cached Gemini client."""

        if not settings.is_gemini_configured:
            raise ValueError(
                "Gemini API key is missing. "
                "Add GEMINI_API_KEY to backend/.env."
            )

        if self._client is None:
            self._client = genai.Client(
                api_key=settings.GEMINI_API_KEY.strip()
            )

        return self._client

    def test_connection(self) -> Dict[str, Any]:
        """Check whether ARI can communicate with Gemini."""

        if not settings.is_gemini_configured:
            return {
                "success": False,
                "status": "not_configured",
                "message": "Gemini API key is missing.",
                "latency_ms": None,
                "model": settings.GEMINI_MODEL,
            }

        start_time = time.time()

        try:
            response = self._get_client().models.generate_content(
                model=settings.GEMINI_MODEL,
                contents="Reply with exactly ARI_DIAGNOSTIC_OK.",
            )

            elapsed_ms = round(
                (time.time() - start_time) * 1000, 2
            )

            output = response.text or ""

            if not output.strip():
                return {
                    "success": False,
                    "status": "empty_response",
                    "message": "Gemini returned an empty response.",
                    "latency_ms": elapsed_ms,
                    "model": settings.GEMINI_MODEL,
                }

            return {
                "success": True,
                "status": "connected",
                "message": (
                    f"Successfully connected to Gemini "
                    f"({settings.GEMINI_MODEL})."
                ),
                "latency_ms": elapsed_ms,
                "model": settings.GEMINI_MODEL,
            }

        except errors.APIError as exc:
            logger.error("Gemini API diagnostic failed: %s", str(exc))

            return {
                "success": False,
                "status": "api_error",
                "message": f"Gemini API error: {str(exc)}",
                "latency_ms": None,
                "model": settings.GEMINI_MODEL,
            }

        except Exception as exc:
            logger.exception("Unexpected Gemini diagnostic error")

            return {
                "success": False,
                "status": "unexpected_error",
                "message": str(exc),
                "latency_ms": None,
                "model": settings.GEMINI_MODEL,
            }

    def generate_response(
        self,
        formatted_prompt: str,
        custom_instructions: Optional[str] = None,
        max_retries: int = 3,
    ) -> str:
        """Generate an answer using Gemini with retry handling."""

        client = self._get_client()

        instructions = (
            custom_instructions or ARI_SYSTEM_INSTRUCTIONS
        )

        for attempt in range(max_retries):

            try:
                logger.info(
                    "Sending request to Gemini (%s), attempt %d/%d",
                    settings.GEMINI_MODEL,
                    attempt + 1,
                    max_retries,
                )

                response = client.models.generate_content(
                    model=settings.GEMINI_MODEL,
                    contents=formatted_prompt,
                    config=genai.types.GenerateContentConfig(
                        system_instruction=instructions,
                        temperature=0.3,
                    ),
                )

                output = response.text

                if output and output.strip():
                    return output.strip()

                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            
            except errors.APIError as exc:

                status_code = getattr(exc, "code", None)
                error_message = str(exc)
                error_lower = error_message.lower()

                logger.warning(
                    "Gemini API error %s on attempt %d: %s",
                    status_code,
                    attempt + 1,
                    error_message,
                )

                # Daily quota exhaustion cannot be fixed by retrying.
                quota_exhausted = (
                    status_code == 429
                    and (
                        "per day" in error_lower
                        or "daily quota" in error_lower
                        or "requestsperday" in error_lower
                        or "limit exceeded" in error_lower
                    )
                )

                if quota_exhausted:
                    logger.error(
                        "Gemini daily quota exhausted. "
                        "Stopping retries immediately."
                    )
                    raise RuntimeError(
                        "ARI's Gemini API daily quota has been "
                        "exhausted. Please check your Gemini API "
                        "usage and billing, or wait for the quota "
                        "to reset."
                    ) from exc

                # Retry temporary errors only.
                retryable = status_code in (
                    429, 500, 502, 503, 504
                )

                if not retryable or attempt == max_retries - 1:
                    raise RuntimeError(
                        f"Gemini API request failed: {error_message}"
                    ) from exc

                wait_time = 2 ** attempt

                logger.info(
                    "Retrying Gemini request in %d seconds.",
                    wait_time,
                )

                time.sleep(wait_time)

        raise RuntimeError(
            "Gemini could not generate a response after retries."
        )


gemini_service = GeminiService()

# Temporary compatibility alias for existing ARI imports.
grok_service = gemini_service

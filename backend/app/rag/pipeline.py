
"""Complete multilingual RAG pipeline using Gemini for answer generation."""

from typing import Dict, Any, List, Optional

from app.core.config import settings
from app.core.logging import logger
from app.core.security import build_safe_rag_prompt
from app.services.gemini import gemini_service, ARI_SYSTEM_INSTRUCTIONS
from app.services.language_service import language_service
from app.rag.vector_store import vector_store
from app.models.schemas import DocumentCitation


# Language-specific insufficient-context messages
INSUFFICIENT_CONTEXT_MESSAGES = {
    "en": (
        "I searched through your uploaded knowledge base, but I couldn't "
        "find sufficiently relevant information to answer this question "
        "accurately. Please consider adding more documents covering this topic."
    ),
    "hi": (
        "मैंने आपके अपलोड किए गए दस्तावेज़ों में खोज की, लेकिन इस प्रश्न का "
        "सटीक उत्तर देने के लिए पर्याप्त प्रासंगिक जानकारी नहीं मिली। "
        "कृपया इस विषय से संबंधित और दस्तावेज़ अपलोड करें।"
    ),
    "mr": (
        "मी तुम्ही अपलोड केलेल्या दस्तऐवजांमध्ये शोध घेतला, परंतु या प्रश्नाचे "
        "अचूक उत्तर देण्यासाठी पुरेशी संबंधित माहिती मिळाली नाही. "
        "कृपया या विषयाशी संबंधित आणखी दस्तऐवज अपलोड करा."
    ),
    "bn": (
        "আমি আপনার আপলোড করা নথিগুলিতে অনুসন্ধান করেছি, কিন্তু এই প্রশ্নের "
        "সঠিক উত্তর দেওয়ার জন্য যথেষ্ট প্রাসঙ্গিক তথ্য পাইনি। "
        "অনুগ্রহ করে এই বিষয়ে আরও নথি আপলোড করুন।"
    ),
    "ta": (
        "நீங்கள் பதிவேற்றிய ஆவணங்களில் தேடினேன், ஆனால் இந்தக் கேள்விக்கு "
        "துல்லியமாகப் பதிலளிக்கப் போதுமான தொடர்புடைய தகவல்கள் கிடைக்கவில்லை. "
        "இந்தத் தலைப்பைப் பற்றிய மேலும் ஆவணங்களைப் பதிவேற்றவும்."
    ),
    "te": (
        "మీరు అప్‌లోడ్ చేసిన పత్రాలలో వెతికాను, కానీ ఈ ప్రశ్నకు ఖచ్చితంగా "
        "సమాధానం ఇవ్వడానికి తగిన సంబంధిత సమాచారం లభించలేదు. "
        "దయచేసి ఈ అంశానికి సంబంధించిన మరిన్ని పత్రాలను అప్‌లోడ్ చేయండి."
    ),
    "es": (
        "He buscado en los documentos que has subido, pero no he encontrado "
        "información suficientemente relevante para responder con precisión. "
        "Por favor, considera subir más documentos sobre este tema."
    ),
    "fr": (
        "J'ai recherché dans vos documents, mais je n'ai pas trouvé "
        "suffisamment d'informations pertinentes pour répondre avec précision. "
        "Veuillez ajouter d'autres documents sur ce sujet."
    ),
    "de": (
        "Ich habe Ihre hochgeladenen Dokumente durchsucht, aber nicht genügend "
        "relevante Informationen gefunden, um diese Frage genau zu beantworten. "
        "Bitte laden Sie weitere Dokumente zu diesem Thema hoch."
    ),
    "ar": (
        "لقد بحثت في المستندات التي قمت بتحميلها، لكنني لم أجد معلومات "
        "ذات صلة كافية للإجابة عن هذا السؤال بدقة. "
        "يرجى تحميل المزيد من المستندات حول هذا الموضوع."
    ),
}


class RAGPipeline:

    def __init__(self):
        pass

    def execute_rag(
        self,
        query: str,
        kb_id: str = "default",
        conversation_history: Optional[List[Dict[str, str]]] = None,
        use_general_knowledge: bool = False,
    ) -> Dict[str, Any]:
        """
        Executes the complete RAG workflow:

        1. Detect the user's language.
        2. Retrieve relevant document chunks.
        3. Validate retrieval results.
        4. Construct a grounded prompt.
        5. Generate an answer using Gemini.
        6. Return the answer with citations.
        """

        # Step 1: Detect query language
        detected_lang = language_service.detect_language(query)
        lang_info = language_service.get_language_info(detected_lang)

        logger.info(
            "Processing query in language '%s' (%s): '%s'...",
            detected_lang,
            lang_info["name"],
            query[:50],
        )

        # Step 2: Retrieve relevant document chunks
        retrieved_chunks = vector_store.search(
            kb_id=kb_id,
            query=query,
            top_k=settings.TOP_K_RESULTS,
            threshold=settings.SIMILARITY_THRESHOLD,
        )

        logger.info(
            "Retrieved %d qualifying chunks above threshold %.2f.",
            len(retrieved_chunks),
            settings.SIMILARITY_THRESHOLD,
        )

        # Step 3: Build document citations
        citations: List[DocumentCitation] = []

        for chunk in retrieved_chunks:
            citations.append(
                DocumentCitation(
                    document_id=chunk["document_id"],
                    document_name=chunk["document_name"],
                    page_number=chunk.get("page_number"),
                    chunk_id=chunk["chunk_id"],
                    snippet=(
                        chunk["text"][:300]
                        + ("..." if len(chunk["text"]) > 300 else "")
                    ),
                    similarity_score=chunk["similarity_score"],
                )
            )

        # Step 4: Handle insufficient context
        if not retrieved_chunks and not use_general_knowledge:

            logger.info(
                "No chunks matched similarity threshold %.2f.",
                settings.SIMILARITY_THRESHOLD,
            )

            insufficient_msg = INSUFFICIENT_CONTEXT_MESSAGES.get(
                detected_lang,
                INSUFFICIENT_CONTEXT_MESSAGES["en"],
            )

            return {
                "answer": insufficient_msg,
                "detected_language": detected_lang,
                "citations": [],
                "retrieval_used": False,
                "context_chunks_retrieved": 0,
                "model": settings.GEMINI_MODEL,
            }

        # Step 5: Verify Gemini configuration
        if not settings.is_gemini_configured:

            logger.warning("Gemini API key is not configured.")

            warning_msg = (
                "Your Gemini API key has not been configured in backend/.env. "
                "Document retrieval succeeded, but generating an answer "
                "requires a valid Gemini API key."
            )

            return {
                "answer": warning_msg,
                "detected_language": detected_lang,
                "citations": citations,
                "retrieval_used": bool(retrieved_chunks),
                "context_chunks_retrieved": len(retrieved_chunks),
                "model": settings.GEMINI_MODEL,
            }

        # Step 6: Construct the RAG prompt
        formatted_prompt = build_safe_rag_prompt(
            query,
            retrieved_chunks,
        )

        # Add recent conversation history
        if conversation_history:

            history_lines = ["\n<recent_conversation_history>"]

            for msg in conversation_history[-4:]:

                role = msg.get("role", "user").capitalize()
                message_text = msg.get("content", "").strip()

                history_lines.append(
                    f"{role}: {message_text}"
                )

            history_lines.append("</recent_conversation_history>\n")

            formatted_prompt = (
                "\n".join(history_lines)
                + "\n"
                + formatted_prompt
            )

        # Step 7: Customize instructions for language
        custom_instructions = (
            f"{ARI_SYSTEM_INSTRUCTIONS}\n\n"
            f"IMPORTANT: The user is communicating in "
            f"{lang_info['name']} "
            f"(Language Code: {detected_lang}). "
            f"You MUST formulate your complete response in "
            f"{lang_info['name']}."
        )

        # General knowledge fallback
        if use_general_knowledge and not retrieved_chunks:

            custom_instructions += (
                "\nNo matching documents were found in the uploaded "
                "knowledge base. You may answer using general knowledge, "
                "but clearly state in your first sentence that the "
                "response is based on general knowledge rather than "
                "uploaded documents."
            )

        # Step 8: Generate answer using Gemini
        logger.info("Sending RAG prompt to Gemini...")

        try:

            answer = gemini_service.generate_response(
                formatted_prompt=formatted_prompt,
                custom_instructions=custom_instructions,
            )

        except Exception as e:

            logger.error(
                "Gemini generation error: %s",
                str(e),
            )

            raise RuntimeError(
                f"Gemini API Error: {str(e)}"
            ) from e

        # Step 9: Return answer and metadata
        return {
            "answer": answer,
            "detected_language": detected_lang,
            "citations": citations,
            "retrieval_used": bool(retrieved_chunks),
            "context_chunks_retrieved": len(retrieved_chunks),
            "model": settings.GEMINI_MODEL,
        }


rag_pipeline = RAGPipeline()


from google import genai
from typing import Optional, Dict, Any
from enum import Enum
from datetime import date, datetime
from sqlalchemy.orm import Session
from app.core.config import settings
from app.services.rag_service import rag_service
from app.database.models import AIModelUsage
from app.database.connection import SessionLocal

class GeminiModel(Enum):
    """Available Gemini models with their daily limits and characteristics"""
    PRO = {
        "name": "gemini-2.5-pro",
        "daily_limit": 100,
        "priority": 1,
        "use_case": "complex_analysis"
    }
    FLASH_PREVIEW = {
        "name": "gemini-2.5-flash-preview-09-2025",
        "daily_limit": 250,
        "priority": 2,
        "use_case": "general_chat"
    }
    FLASH = {
        "name": "gemini-2.5-flash",
        "daily_limit": 250,
        "priority": 3,
        "use_case": "general_chat"
    }
    FLASH_LITE = {
        "name": "gemini-2.5-flash-lite",
        "daily_limit": 1000,
        "priority": 4,
        "use_case": "simple_queries"
    }

class AIService:
    def __init__(self):
        self.gemini_api_key = settings.gemini_api_key
        self.client = None

    def _get_client(self):
        """Lazy initialization of Gemini client"""
        if self.client is None and self.gemini_api_key:
            try:
                # Use direct API key parameter (proven to work)
                self.client = genai.Client(api_key=self.gemini_api_key)
            except Exception as e:
                print(f"Failed to create Gemini client with direct API key: {e}")
                return None
        return self.client

    def _get_usage_for_date(self, db: Session, model_name: str, target_date: date) -> int:
        """Get current usage count for a model on a specific date"""
        usage = db.query(AIModelUsage).filter(
            AIModelUsage.model_name == model_name,
            AIModelUsage.date == target_date
        ).first()
        return usage.request_count if usage else 0

    def _increment_usage(self, db: Session, model_name: str) -> None:
        """Increment usage count for a model today"""
        today = date.today()
        usage = db.query(AIModelUsage).filter(
            AIModelUsage.model_name == model_name,
            AIModelUsage.date == today
        ).first()

        if usage:
            usage.request_count += 1
            usage.updated_at = datetime.utcnow()
        else:
            usage = AIModelUsage(
                model_name=model_name,
                request_count=1,
                date=today
            )
            db.add(usage)
        db.commit()

    def _select_best_available_model(self, complexity: str = "general") -> Optional[GeminiModel]:
        """Select the best available model based on complexity and current usage"""
        db = SessionLocal()
        try:
            today = date.today()

            # Determine preferred models based on complexity
            if complexity == "complex":
                # For complex tasks, prefer Pro > Flash Preview > Flash > Flash-Lite
                preferred_order = [GeminiModel.PRO, GeminiModel.FLASH_PREVIEW, GeminiModel.FLASH, GeminiModel.FLASH_LITE]
            elif complexity == "simple":
                # For simple tasks, prefer Flash-Lite > Flash > Flash Preview > Pro (save quota)
                preferred_order = [GeminiModel.FLASH_LITE, GeminiModel.FLASH, GeminiModel.FLASH_PREVIEW, GeminiModel.PRO]
            else:
                # For general tasks, prefer Flash Preview > Flash > Pro > Flash-Lite
                preferred_order = [GeminiModel.FLASH_PREVIEW, GeminiModel.FLASH, GeminiModel.PRO, GeminiModel.FLASH_LITE]

            # Find first available model with quota remaining
            for model in preferred_order:
                current_usage = self._get_usage_for_date(db, model.value["name"], today)
                if current_usage < model.value["daily_limit"]:
                    return model

            # If all models are at limit, return None
            return None
        finally:
            db.close()

    def get_usage_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get current usage statistics for all models"""
        db = SessionLocal()
        try:
            today = date.today()
            stats = {}

            for model in GeminiModel:
                model_name = model.value["name"]
                current_usage = self._get_usage_for_date(db, model_name, today)
                daily_limit = model.value["daily_limit"]

                stats[model_name] = {
                    "current_usage": current_usage,
                    "daily_limit": daily_limit,
                    "remaining": daily_limit - current_usage,
                    "percentage_used": round((current_usage / daily_limit) * 100, 1),
                    "priority": model.value["priority"],
                    "use_case": model.value["use_case"]
                }

            return stats
        finally:
            db.close()

    async def translate_crochet_pattern(self, pattern_text: str, user_context: str = "") -> str:
        """
        Translate crochet pattern notation into readable instructions using best available model
        """
        client = self._get_client()
        if client:
            # Pattern translation is complex, prefer higher-tier models
            return await self._translate_with_gemini(pattern_text, user_context, complexity="complex")
        else:
            return self._fallback_translation(pattern_text)

    async def chat_about_pattern(self, message: str, project_context: str = "", chat_history: str = "") -> str:
        """
        Chat with AI about crochet patterns and techniques using best available model
        """
        client = self._get_client()
        if client:
            # Determine complexity based on message content
            complexity = self._analyze_message_complexity(message)
            return await self._chat_with_gemini(message, project_context, chat_history, complexity=complexity)
        else:
            return "AI service not configured. Please set GEMINI_API_KEY."

    def _analyze_message_complexity(self, message: str) -> str:
        """Analyze message to determine appropriate model complexity"""
        message_lower = message.lower()

        # Complex indicators
        complex_keywords = [
            "diagram", "chart", "pattern", "translate", "convert",
            "calculate", "design", "modify", "complex", "advanced"
        ]

        # Simple indicators
        simple_keywords = [
            "what is", "define", "meaning", "abbreviation", "mean",
            "hello", "hi", "thanks", "thank you"
        ]

        if any(keyword in message_lower for keyword in complex_keywords):
            return "complex"
        elif any(keyword in message_lower for keyword in simple_keywords):
            return "simple"
        else:
            return "general"

    async def _translate_with_gemini(self, pattern_text: str, context: str, complexity: str = "complex") -> str:
        """Use best available Gemini model for pattern translation"""
        try:
            # Select best available model
            selected_model = self._select_best_available_model(complexity)
            if not selected_model:
                return "All AI models have reached their daily limits. Please try again tomorrow."

            model_name = selected_model.value["name"]

            system_prompt = """You are an expert crochet instructor. Your job is to translate standard crochet notation into clear, easy-to-follow instructions for beginners and intermediate crocheters.

Rules for translation:
- Expand all abbreviations (sc = single crochet, dc = double crochet, etc.)
- Break down complex instructions into numbered steps
- Explain stitch counts and placement clearly
- Add helpful tips for tricky techniques
- Use encouraging, friendly language
- Include warnings about common mistakes"""

            user_prompt = f"""Please translate this crochet pattern into clear, step-by-step instructions:

PATTERN:
{pattern_text}

{f'CONTEXT: {context}' if context else ''}

Provide detailed, beginner-friendly instructions."""

            # Combine system and user prompts for Gemini
            combined_prompt = f"{system_prompt}\n\n{user_prompt}"

            client = self._get_client()
            response = client.models.generate_content(
                model=model_name,
                contents=combined_prompt
            )

            # Track usage
            db = SessionLocal()
            try:
                self._increment_usage(db, model_name)
            finally:
                db.close()

            return f"[{model_name}] {response.text}"

        except Exception as e:
            return f"Error translating pattern: {str(e)}"

    async def _chat_with_gemini(self, message: str, project_context: str, chat_history: str, complexity: str = "general") -> str:
        """Use best available Gemini model for crochet chat with RAG enhancement"""
        try:
            # Select best available model
            selected_model = self._select_best_available_model(complexity)
            if not selected_model:
                return "All AI models have reached their daily limits. Please try again tomorrow."

            model_name = selected_model.value["name"]

            # Use RAG to analyze user request and enhance context
            user_analysis = rag_service.analyze_user_request(message)

            # Base system prompt
            system_prompt = """You are a friendly, expert crochet instructor and pattern designer. Help users with:
- Crochet technique questions
- Pattern interpretation and clarification
- Troubleshooting common problems
- Yarn and hook recommendations
- Project planning and modifications
- Stitch counting and pattern adjustments

CRITICAL DIAGRAM CAPABILITIES:
You can generate professional crochet charts! When users request diagrams, you will create authentic crochet charts with:
- Proper international crochet symbols (X for sc, T-with-bars for dc/hdc)
- Radial guidelines showing stitch placement from center outward
- Curved directional arrows indicating counterclockwise work flow
- Professional circular layout for round-based patterns
- Traditional black symbols on white background with colored directional elements

When users ask for diagrams, be confident and explain that you'll create a professional crochet chart for them. Never say you can't create diagrams - you absolutely can and will create industry-standard crochet charts!

Always be encouraging and provide practical, actionable advice."""

            # Enhance context with RAG if diagram is requested
            context_info = ""
            if project_context:
                context_info += f"\nCURRENT PROJECT CONTEXT:\n{project_context}\n"
            if chat_history:
                context_info += f"\nPREVIOUS CONVERSATION:\n{chat_history}\n"

            # Add RAG enhancement for diagram requests
            if user_analysis['requests_diagram']:
                # Extract any pattern from the message for RAG enhancement
                pattern_text = message if any(pe in message.lower() for pe in ['round', 'row', 'chain', 'dc', 'sc']) else ""
                if pattern_text:
                    rag_enhancement = rag_service.enhance_pattern_context(pattern_text, message)
                    context_info += f"\n{rag_enhancement}\n"

            user_prompt = f"{context_info}\nUSER QUESTION: {message}"

            # Combine system and user prompts for Gemini
            combined_prompt = f"{system_prompt}\n\n{user_prompt}"

            client = self._get_client()
            response = client.models.generate_content(
                model=model_name,
                contents=combined_prompt
            )

            # Track usage
            db = SessionLocal()
            try:
                self._increment_usage(db, model_name)
            finally:
                db.close()

            return f"[{model_name}] {response.text}"

        except Exception as e:
            return f"Sorry, I'm having trouble responding right now: {str(e)}"


    def _fallback_translation(self, pattern_text: str) -> str:
        """Basic pattern translation without AI"""
        # Simple abbreviation expansion as fallback
        abbreviations = {
            'sc': 'single crochet',
            'dc': 'double crochet',
            'hdc': 'half double crochet',
            'tc': 'treble crochet',
            'sl st': 'slip stitch',
            'ch': 'chain',
            'st': 'stitch',
            'sts': 'stitches',
            'inc': 'increase',
            'dec': 'decrease',
            'yo': 'yarn over',
            'sk': 'skip',
            'rep': 'repeat',
            'rnd': 'round',
            'beg': 'beginning',
            'sp': 'space',
            'tog': 'together'
        }

        translated = pattern_text
        for abbrev, full_form in abbreviations.items():
            translated = translated.replace(abbrev, full_form)

        return f"Basic translation (AI not available):\n\n{translated}\n\nNote: This is a simple translation. For detailed instructions, please configure AI service."

# Global instance
ai_service = AIService()
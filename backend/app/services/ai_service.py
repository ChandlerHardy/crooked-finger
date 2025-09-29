from google import genai
from typing import Optional
from app.core.config import settings
from app.services.rag_service import rag_service

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

    async def translate_crochet_pattern(self, pattern_text: str, user_context: str = "") -> str:
        """
        Translate crochet pattern notation into readable instructions using Gemini
        """
        client = self._get_client()
        if client:
            return await self._translate_with_gemini(pattern_text, user_context)
        else:
            return self._fallback_translation(pattern_text)

    async def chat_about_pattern(self, message: str, project_context: str = "", chat_history: str = "") -> str:
        """
        Chat with AI about crochet patterns and techniques using Gemini
        """
        client = self._get_client()
        if client:
            return await self._chat_with_gemini(message, project_context, chat_history)
        else:
            return "AI service not configured. Please set GEMINI_API_KEY."

    async def _translate_with_gemini(self, pattern_text: str, context: str) -> str:
        """Use Google Gemini for pattern translation"""
        try:
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
                model="gemini-2.5-flash",
                contents=combined_prompt
            )
            return response.text
        except Exception as e:
            return f"Error translating pattern: {str(e)}"

    async def _chat_with_gemini(self, message: str, project_context: str, chat_history: str) -> str:
        """Use Google Gemini for crochet chat with RAG enhancement"""
        try:
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
                model="gemini-2.5-flash",
                contents=combined_prompt
            )
            return response.text
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
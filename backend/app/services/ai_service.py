import httpx
from typing import Optional
from app.core.config import settings

class AIService:
    def __init__(self):
        self.github_token = settings.github_token
        self.openai_api_key = settings.openai_api_key

    async def translate_crochet_pattern(self, pattern_text: str, user_context: str = "") -> str:
        """
        Translate crochet pattern notation into readable instructions
        """
        if self.github_token:
            return await self._translate_with_github_llama(pattern_text, user_context)
        elif self.openai_api_key:
            return await self._translate_with_openai(pattern_text, user_context)
        else:
            return self._fallback_translation(pattern_text)

    async def chat_about_pattern(self, message: str, project_context: str = "", chat_history: str = "") -> str:
        """
        Chat with AI about crochet patterns and techniques
        """
        if self.github_token:
            return await self._chat_with_github_llama(message, project_context, chat_history)
        elif self.openai_api_key:
            return await self._chat_with_openai(message, project_context, chat_history)
        else:
            return "AI service not configured. Please set GITHUB_TOKEN or OPENAI_API_KEY."

    async def _translate_with_github_llama(self, pattern_text: str, context: str) -> str:
        """Use GitHub's Llama model for pattern translation"""
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

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://models.github.ai/inference",
                    headers={
                        "Authorization": f"Bearer {self.github_token}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "llama-3.1-8b-instruct",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "max_tokens": 1000,
                        "temperature": 0.7
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error translating pattern: {str(e)}"

    async def _chat_with_github_llama(self, message: str, project_context: str, chat_history: str) -> str:
        """Use GitHub's Llama model for crochet chat"""
        try:
            system_prompt = """You are a friendly, expert crochet instructor and pattern designer. Help users with:
- Crochet technique questions
- Pattern interpretation and clarification
- Troubleshooting common problems
- Yarn and hook recommendations
- Project planning and modifications
- Stitch counting and pattern adjustments

Always be encouraging and provide practical, actionable advice."""

            context_info = ""
            if project_context:
                context_info += f"\nCURRENT PROJECT CONTEXT:\n{project_context}\n"
            if chat_history:
                context_info += f"\nPREVIOUS CONVERSATION:\n{chat_history}\n"

            user_prompt = f"{context_info}\nUSER QUESTION: {message}"

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://models.github.ai/inference",
                    headers={
                        "Authorization": f"Bearer {self.github_token}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "llama-3.1-8b-instruct",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "max_tokens": 800,
                        "temperature": 0.8
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Sorry, I'm having trouble responding right now: {str(e)}"

    async def _translate_with_openai(self, pattern_text: str, context: str) -> str:
        """Use OpenAI for pattern translation"""
        # TODO: Implement OpenAI integration if needed
        return "OpenAI integration not implemented yet."

    async def _chat_with_openai(self, message: str, project_context: str, chat_history: str) -> str:
        """Use OpenAI for crochet chat"""
        # TODO: Implement OpenAI integration if needed
        return "OpenAI integration not implemented yet."

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
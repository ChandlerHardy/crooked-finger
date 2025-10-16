from google import genai
from google.genai import types
from typing import Optional, Dict, Any
from enum import Enum
from datetime import date, datetime
from sqlalchemy.orm import Session
from app.core.config import settings
from app.services.rag_service import rag_service
from app.database.models import AIModelUsage
from app.database.connection import SessionLocal
import httpx
import json
import base64

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
    # All available models
    ALL_AVAILABLE_MODELS = {
        # OpenRouter free models
        "deepseek/deepseek-chat-v3.1:free": {"provider": "openrouter", "name": "DeepSeek Chat v3.1", "cost": "free"},
        "qwen/qwen3-30b-a3b:free": {"provider": "openrouter", "name": "Qwen3 30B A3B (Often Unavailable)", "cost": "free"},
        # Gemini models
        "gemini-2.5-pro": {"provider": "gemini", "name": "Gemini 2.5 Pro", "daily_limit": 100},
        "gemini-2.5-flash-preview-09-2025": {"provider": "gemini", "name": "Gemini 2.5 Flash Preview", "daily_limit": 250},
        "gemini-2.5-flash": {"provider": "gemini", "name": "Gemini 2.5 Flash", "daily_limit": 250},
        "gemini-2.5-flash-lite": {"provider": "gemini", "name": "Gemini 2.5 Flash Lite", "daily_limit": 1000},
    }

    # Default OpenRouter model priority (will try in order)
    # Note: Qwen removed from default as it's frequently unavailable (503 errors)
    DEFAULT_OPENROUTER_MODELS = [
        "deepseek/deepseek-chat-v3.1:free",  # Primary: DeepSeek v3.1 (unlimited, reliable)
    ]

    def __init__(self):
        self.gemini_api_key = settings.gemini_api_key
        self.openrouter_api_key = getattr(settings, 'openrouter_api_key', None)
        self.client = None

        # Load persisted configuration from database
        self._load_config_from_db()

        # If no config in DB, use defaults
        if not hasattr(self, '_selected_model'):
            self.use_openrouter_default = False  # Don't default to OpenRouter
            self._ai_provider_preference = "auto"  # "openrouter", "gemini", or "auto"
            self._selected_model = None  # Specific model or None for smart routing
            self._model_priority_order = []  # Empty = smart routing, not fallback

    def _load_config_from_db(self):
        """Load AI model configuration from database"""
        from app.database.models import AIModelConfig
        db = SessionLocal()
        try:
            config = db.query(AIModelConfig).first()
            if config:
                self._selected_model = config.selected_model
                self._model_priority_order = config.model_priority_order or []
                self._ai_provider_preference = config.provider_preference or "auto"

                # Set use_openrouter_default based on configuration
                if self._selected_model:
                    model_info = self.ALL_AVAILABLE_MODELS.get(self._selected_model)
                    self.use_openrouter_default = model_info and model_info["provider"] == "openrouter"
                elif self._model_priority_order:
                    self.use_openrouter_default = True
                else:
                    self.use_openrouter_default = False
        except Exception as e:
            # Table may not exist yet (before migration runs)
            print(f"Could not load AI config from database (table may not exist yet): {e}")
            pass
        finally:
            db.close()

    def _save_config_to_db(self):
        """Save AI model configuration to database"""
        from app.database.models import AIModelConfig
        db = SessionLocal()
        try:
            config = db.query(AIModelConfig).first()
            if not config:
                config = AIModelConfig()
                db.add(config)

            config.selected_model = self._selected_model
            config.model_priority_order = self._model_priority_order
            config.provider_preference = self._ai_provider_preference
            config.updated_at = datetime.utcnow()

            db.commit()
        finally:
            db.close()

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

    def _increment_usage(self, db: Session, model_name: str, input_chars: int = 0, output_chars: int = 0) -> None:
        """Increment usage count for a model today with character/token tracking"""
        today = date.today()
        usage = db.query(AIModelUsage).filter(
            AIModelUsage.model_name == model_name,
            AIModelUsage.date == today
        ).first()

        # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
        input_tokens = input_chars // 4
        output_tokens = output_chars // 4

        if usage:
            usage.request_count += 1
            usage.total_input_characters += input_chars
            usage.total_output_characters += output_chars
            usage.total_input_tokens += input_tokens
            usage.total_output_tokens += output_tokens
            usage.updated_at = datetime.utcnow()
        else:
            usage = AIModelUsage(
                model_name=model_name,
                request_count=1,
                total_input_characters=input_chars,
                total_output_characters=output_chars,
                total_input_tokens=input_tokens,
                total_output_tokens=output_tokens,
                date=today
            )
            db.add(usage)
        db.commit()

    def reset_daily_usage(self) -> Dict[str, Any]:
        """Reset all AI model usage for today"""
        db = SessionLocal()
        try:
            today = date.today()

            # Delete all usage records for today
            deleted_count = db.query(AIModelUsage).filter(
                AIModelUsage.date == today
            ).delete()

            db.commit()

            return {
                "success": True,
                "message": f"Reset usage for {deleted_count} model entries on {today}",
                "reset_date": today.isoformat()
            }

        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "message": f"Failed to reset usage: {str(e)}",
                "reset_date": None
            }
        finally:
            db.close()

    def _select_best_available_model(self, complexity: str = "general") -> Optional[GeminiModel]:
        """Select the best available model based on complexity and current usage"""
        db = SessionLocal()
        try:
            today = date.today()

            # Determine preferred models based on complexity
            # Flash-Lite is always last resort due to lower quality
            if complexity == "complex":
                # For complex tasks, prefer Pro > Flash Preview > Flash > Flash-Lite
                preferred_order = [GeminiModel.PRO, GeminiModel.FLASH_PREVIEW, GeminiModel.FLASH, GeminiModel.FLASH_LITE]
            elif complexity == "simple":
                # For simple tasks, prefer Flash > Flash Preview > Pro > Flash-Lite (Flash is efficient)
                preferred_order = [GeminiModel.FLASH, GeminiModel.FLASH_PREVIEW, GeminiModel.PRO, GeminiModel.FLASH_LITE]
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

            # Add Gemini models
            for model in GeminiModel:
                model_name = model.value["name"]
                usage_record = db.query(AIModelUsage).filter(
                    AIModelUsage.model_name == model_name,
                    AIModelUsage.date == today
                ).first()

                current_usage = usage_record.request_count if usage_record else 0
                daily_limit = model.value["daily_limit"]

                stats[model_name] = {
                    "current_usage": current_usage,
                    "daily_limit": daily_limit,
                    "remaining": daily_limit - current_usage,
                    "percentage_used": round((current_usage / daily_limit) * 100, 1),
                    "priority": model.value["priority"],
                    "use_case": model.value["use_case"],
                    "total_input_characters": usage_record.total_input_characters if usage_record else 0,
                    "total_output_characters": usage_record.total_output_characters if usage_record else 0,
                    "total_input_tokens": usage_record.total_input_tokens if usage_record else 0,
                    "total_output_tokens": usage_record.total_output_tokens if usage_record else 0,
                }

            # Add OpenRouter models (unlimited, so always show as available)
            for model_name, info in self.ALL_AVAILABLE_MODELS.items():
                if info["provider"] == "openrouter":
                    usage_record = db.query(AIModelUsage).filter(
                        AIModelUsage.model_name == model_name,
                        AIModelUsage.date == today
                    ).first()

                    current_usage = usage_record.request_count if usage_record else 0

                    stats[model_name] = {
                        "current_usage": current_usage,
                        "daily_limit": 999999,  # Unlimited
                        "remaining": 999999,
                        "percentage_used": 0,
                        "priority": 0,
                        "use_case": "unlimited",
                        "total_input_characters": usage_record.total_input_characters if usage_record else 0,
                        "total_output_characters": usage_record.total_output_characters if usage_record else 0,
                        "total_input_tokens": usage_record.total_input_tokens if usage_record else 0,
                        "total_output_tokens": usage_record.total_output_tokens if usage_record else 0,
                    }

            return stats
        finally:
            db.close()

    async def translate_crochet_pattern(self, pattern_text: str, user_context: str = "") -> str:
        """
        Translate crochet pattern notation into readable instructions using configured model
        """
        # If specific model is selected, use it directly
        if self._selected_model:
            model_info = self.ALL_AVAILABLE_MODELS.get(self._selected_model)
            if model_info:
                if model_info["provider"] == "openrouter":
                    return await self._translate_with_specific_openrouter_model(pattern_text, user_context, self._selected_model)
                elif model_info["provider"] == "gemini":
                    return await self._translate_with_specific_gemini_model(pattern_text, user_context, self._selected_model)

        # If fallback chain is configured (non-empty priority order), use it
        if self._model_priority_order:
            return await self._translate_with_openrouter(pattern_text, user_context)

        # Smart routing: Pattern translation is complex, prefer higher-tier models
        client = self._get_client()
        if client:
            return await self._translate_with_gemini(pattern_text, user_context, complexity="complex")
        else:
            return self._fallback_translation(pattern_text)

    async def chat_about_pattern(self, message: str, project_context: str = "", chat_history: str = "", image_data: Optional[str] = None) -> str:
        """
        Chat with AI about crochet patterns and techniques using configured model
        Supports image analysis when image_data is provided (JSON array of base64 strings)
        """
        # If specific model is selected, use it directly
        if self._selected_model:
            model_info = self.ALL_AVAILABLE_MODELS.get(self._selected_model)
            if model_info:
                if model_info["provider"] == "openrouter":
                    return await self._chat_with_specific_openrouter_model(message, project_context, chat_history, self._selected_model, image_data)
                elif model_info["provider"] == "gemini":
                    return await self._chat_with_specific_gemini_model(message, project_context, chat_history, self._selected_model, image_data)

        # If fallback chain is configured (non-empty priority order), use it
        if self._model_priority_order:
            return await self._chat_with_openrouter(message, project_context, chat_history, image_data)

        # Smart routing: use complexity-based selection
        client = self._get_client()
        if client:
            complexity = self._analyze_message_complexity(message)
            return await self._chat_with_gemini(message, project_context, chat_history, complexity=complexity, image_data=image_data)
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

    def _detect_mime_type(self, data: bytes) -> str:
        """Detect MIME type from file magic bytes"""
        # Check magic bytes (file signatures)
        if data[:4] == b'%PDF':
            return "application/pdf"
        elif data[:2] == b'\xff\xd8':
            return "image/jpeg"
        elif data[:8] == b'\x89PNG\r\n\x1a\n':
            return "image/png"
        elif data[:6] in (b'GIF87a', b'GIF89a'):
            return "image/gif"
        elif data[:2] in (b'BM', b'BA'):
            return "image/bmp"
        elif data[:4] == b'RIFF' and data[8:12] == b'WEBP':
            return "image/webp"
        else:
            # Default to JPEG if unknown (most common for photos)
            print(f"Warning: Unknown file type, defaulting to image/jpeg. First bytes: {data[:10].hex()}")
            return "image/jpeg"

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

            # Track usage with character counts
            db = SessionLocal()
            try:
                input_chars = len(combined_prompt)
                output_chars = len(response.text)
                self._increment_usage(db, model_name, input_chars, output_chars)
            finally:
                db.close()

            return f"[{model_name}] {response.text}"

        except Exception as e:
            return f"Error translating pattern: {str(e)}"

    async def _chat_with_gemini(self, message: str, project_context: str, chat_history: str, complexity: str = "general", image_data: Optional[str] = None) -> str:
        """Use best available Gemini model for crochet chat with RAG enhancement and image support"""
        try:
            # Select best available model
            selected_model = self._select_best_available_model(complexity)
            if not selected_model:
                return "All AI models have reached their daily limits. Please try again tomorrow."

            model_name = selected_model.value["name"]

            # Use RAG to analyze user request and enhance context
            user_analysis = rag_service.analyze_user_request(message)

            # Enhanced system prompt for image analysis
            if image_data:
                system_prompt = """You are an expert crochet instructor and pattern designer. Analyze the image and extract the crochet pattern.

Format your response EXACTLY like this example (do NOT use numbered lists):

NAME: Cat's Cradle Blanket
NOTATION: Foundation Chain: Ch 122. Row 1: Dc in 3rd ch from hook and in each ch across, ch 2, turn — 120 dc. Row 2: Dc in 1st st, *Fpdc around the next 2 sts, Bpdc around the next 2 sts; rep from * to last st, dc in last st, ch 2, turn.
INSTRUCTIONS:
Round 1: Make a magic ring. Chain 2, work 12 double crochet into the ring. Pull the ring tight and slip stitch to join.

Round 2: Chain 2. Work 2 double crochet in each stitch around (24 stitches total). Slip stitch to join.

Round 3: Chain 2. *Work 1 double crochet in the next stitch, then 2 double crochet in the following stitch.* Repeat from * to * around (36 stitches total). Slip stitch to join.

DIFFICULTY: beginner
MATERIALS: Worsted weight yarn (4), 5.5mm (I) crochet hook
TIME: 2-3 hours

CRITICAL FORMATTING RULES:
- Do NOT number your response (no "1.", "2.", "3.")
- Do NOT use markdown bold (**text**)
- Put TWO line breaks between each round in INSTRUCTIONS
- Write INSTRUCTIONS as complete sentences, not abbreviated notation
- Separate each major section with blank lines
- Use the exact header format: "NAME:", "NOTATION:", "INSTRUCTIONS:", etc."""
            else:
                system_prompt = """You are a friendly, expert crochet instructor and pattern designer. Help users with:
- Crochet technique questions
- Pattern interpretation and clarification
- Troubleshooting common problems
- Yarn and hook recommendations
- Project planning and modifications
- Stitch counting and pattern adjustments

Format your responses with clear paragraph breaks for readability.

NOTE: Diagram generation is temporarily disabled. When users ask for visual diagrams or charts, politely explain that you can provide detailed written descriptions of patterns instead, including step-by-step instructions and stitch placement explanations.

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

            # Build contents array with text and images if provided
            if image_data:
                try:
                    image_list = json.loads(image_data)
                    # Create parts list with text and images
                    parts = [combined_prompt]
                    for img_base64 in image_list:
                        # Gemini SDK expects Part objects with inline_data
                        img_bytes = base64.b64decode(img_base64)

                        # Detect MIME type from magic bytes
                        mime_type = self._detect_mime_type(img_bytes)

                        parts.append(types.Part.from_bytes(
                            data=img_bytes,
                            mime_type=mime_type
                        ))
                    contents = parts
                except (json.JSONDecodeError, base64.binascii.Error) as e:
                    print(f"Warning: Failed to parse image data: {e}")
                    contents = combined_prompt
            else:
                contents = combined_prompt

            response = client.models.generate_content(
                model=model_name,
                contents=contents
            )

            # Track usage with character counts
            db = SessionLocal()
            try:
                input_chars = len(combined_prompt)
                output_chars = len(response.text)
                self._increment_usage(db, model_name, input_chars, output_chars)
            finally:
                db.close()

            return f"[{model_name}] {response.text}"

        except Exception as e:
            return f"Sorry, I'm having trouble responding right now: {str(e)}"


    async def _translate_with_openrouter(self, pattern_text: str, context: str) -> str:
        """Use OpenRouter models for pattern translation with fallback"""
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

        # Try each model in configured priority order
        last_error = None
        for model_name in self._model_priority_order:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.openrouter_api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": model_name,
                            "messages": [
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_prompt}
                            ]
                        },
                        timeout=30.0
                    )
                    response.raise_for_status()
                    result = response.json()

                    ai_response = result["choices"][0]["message"]["content"]

                    # Track usage
                    db = SessionLocal()
                    try:
                        input_chars = len(system_prompt) + len(user_prompt)
                        output_chars = len(ai_response)
                        self._increment_usage(db, model_name, input_chars, output_chars)
                    finally:
                        db.close()

                    return f"[{model_name}] {ai_response}"

            except Exception as e:
                last_error = e
                print(f"OpenRouter model {model_name} failed: {e}, trying next model...")
                continue

        # All models failed
        return f"Error with OpenRouter (all models failed): {str(last_error)}"

    async def _chat_with_openrouter(self, message: str, project_context: str, chat_history: str, image_data: Optional[str] = None) -> str:
        """Use OpenRouter models for crochet chat with fallback (image support not yet implemented)"""
        # TODO: Add image support for OpenRouter models that support it
        if image_data:
            print("Warning: Image data provided but OpenRouter image support not yet implemented")
        # Use RAG to analyze user request and enhance context
        user_analysis = rag_service.analyze_user_request(message)

        system_prompt = """You are a friendly, expert crochet instructor and pattern designer. Help users with:
- Crochet technique questions
- Pattern interpretation and clarification
- Troubleshooting common problems
- Yarn and hook recommendations
- Project planning and modifications
- Stitch counting and pattern adjustments

NOTE: Diagram generation is temporarily disabled. When users ask for visual diagrams or charts, politely explain that you can provide detailed written descriptions of patterns instead, including step-by-step instructions and stitch placement explanations.

Always be encouraging and provide practical, actionable advice."""

        # Enhance context with RAG if diagram is requested
        context_info = ""
        if project_context:
            context_info += f"\nCURRENT PROJECT CONTEXT:\n{project_context}\n"
        if chat_history:
            context_info += f"\nPREVIOUS CONVERSATION:\n{chat_history}\n"

        # Add RAG enhancement for diagram requests
        if user_analysis['requests_diagram']:
            pattern_text = message if any(pe in message.lower() for pe in ['round', 'row', 'chain', 'dc', 'sc']) else ""
            if pattern_text:
                rag_enhancement = rag_service.enhance_pattern_context(pattern_text, message)
                context_info += f"\n{rag_enhancement}\n"

        user_prompt = f"{context_info}\nUSER QUESTION: {message}"

        # Try each model in configured priority order
        last_error = None
        for model_name in self._model_priority_order:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.openrouter_api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": model_name,
                            "messages": [
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_prompt}
                            ]
                        },
                        timeout=30.0
                    )
                    response.raise_for_status()
                    result = response.json()

                    ai_response = result["choices"][0]["message"]["content"]

                    # Track usage
                    db = SessionLocal()
                    try:
                        input_chars = len(system_prompt) + len(user_prompt)
                        output_chars = len(ai_response)
                        self._increment_usage(db, model_name, input_chars, output_chars)
                    finally:
                        db.close()

                    return f"[{model_name}] {ai_response}"

            except Exception as e:
                last_error = e
                print(f"OpenRouter model {model_name} failed: {e}, trying next model...")
                continue

        # All models failed
        return f"Sorry, I'm having trouble responding right now: {str(last_error)}"

    async def _translate_with_specific_openrouter_model(self, pattern_text: str, user_context: str, model_name: str) -> str:
        """Translate pattern using a specific OpenRouter model"""
        system_prompt = """You are an expert crochet pattern translator. Convert abbreviated crochet patterns into clear, readable instructions.

Key responsibilities:
- Expand all abbreviations (sc = single crochet, dc = double crochet, etc.)
- Explain stitch placement and technique
- Maintain the original pattern structure (rounds/rows)
- Provide context for complex stitches
- Be precise with stitch counts and placement"""

        user_prompt = f"""Translate this crochet pattern into clear instructions:

{pattern_text}

{f'Additional context: {user_context}' if user_context else ''}

Provide a clear, step-by-step translation."""

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openrouter_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model_name,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ]
                    },
                    timeout=60.0
                )
                response.raise_for_status()
                result = response.json()
                ai_response = result['choices'][0]['message']['content']

                # Track usage
                input_chars = len(system_prompt) + len(user_prompt)
                output_chars = len(ai_response)
                db = SessionLocal()
                try:
                    self._increment_usage(db, model_name, input_chars, output_chars)
                finally:
                    db.close()

                return ai_response

        except Exception as e:
            error_msg = str(e)
            if "503" in error_msg:
                return f"The {model_name} model is currently unavailable. Please try a different model."
            elif "429" in error_msg:
                return f"Rate limit reached for {model_name}. Please try a different model or wait a few minutes."
            else:
                return f"Translation failed with {model_name}: {error_msg}"

    async def _translate_with_specific_gemini_model(self, pattern_text: str, user_context: str, model_name: str) -> str:
        """Translate pattern using a specific Gemini model"""
        system_instruction = """You are an expert crochet pattern translator. Convert abbreviated crochet patterns into clear, readable instructions.

Key responsibilities:
- Expand all abbreviations (sc = single crochet, dc = double crochet, etc.)
- Explain stitch placement and technique
- Maintain the original pattern structure (rounds/rows)
- Provide context for complex stitches
- Be precise with stitch counts and placement"""

        user_prompt = f"""Translate this crochet pattern into clear instructions:

{pattern_text}

{f'Additional context: {user_context}' if user_context else ''}

Provide a clear, step-by-step translation."""

        try:
            client = self._get_client()
            if not client:
                return "Gemini client not configured"

            response = client.models.generate_content(
                model=model_name,
                contents=user_prompt,
                config={
                    "system_instruction": system_instruction,
                    "temperature": 0.3,
                }
            )

            ai_response = response.text

            # Track usage
            input_chars = len(system_instruction) + len(user_prompt)
            output_chars = len(ai_response)
            db = SessionLocal()
            try:
                self._increment_usage(db, model_name, input_chars, output_chars)
            finally:
                db.close()

            return ai_response

        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower():
                return f"Daily quota reached for {model_name}. Please try a different model or wait until tomorrow."
            else:
                return f"Translation failed with {model_name}: {error_msg}"

    async def _chat_with_specific_openrouter_model(self, message: str, project_context: str, chat_history: str, model_name: str, image_data: Optional[str] = None) -> str:
        """Chat using a specific OpenRouter model (image support not yet implemented)"""
        # TODO: Add image support for OpenRouter models that support it
        if image_data:
            print("Warning: Image data provided but OpenRouter image support not yet implemented")
        user_analysis = rag_service.analyze_user_request(message)

        system_prompt = """You are a friendly, expert crochet instructor and pattern designer. Help users with:
- Crochet technique questions
- Pattern interpretation and clarification
- Troubleshooting common problems
- Yarn and hook recommendations
- Project planning and modifications
- Stitch counting and pattern adjustments

NOTE: Diagram generation is temporarily disabled. When users ask for visual diagrams or charts, politely explain that you can provide detailed written descriptions of patterns instead, including step-by-step instructions and stitch placement explanations.

Always be encouraging and provide practical, actionable advice."""

        context_info = ""
        if project_context:
            context_info += f"\nCURRENT PROJECT CONTEXT:\n{project_context}\n"
        if chat_history:
            context_info += f"\nPREVIOUS CONVERSATION:\n{chat_history}\n"

        if user_analysis['requests_diagram']:
            pattern_text = message if any(pe in message.lower() for pe in ['round', 'row', 'chain', 'dc', 'sc']) else ""
            if pattern_text:
                rag_enhancement = rag_service.enhance_pattern_context(pattern_text, message)
                context_info += f"\n{rag_enhancement}\n"

        user_prompt = f"{context_info}\nUSER QUESTION: {message}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openrouter_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model_name,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ]
                    },
                    timeout=60.0
                )
                response.raise_for_status()
                result = response.json()
                ai_response = result['choices'][0]['message']['content']

                # Track usage
                input_chars = len(system_prompt) + len(user_prompt)
                output_chars = len(ai_response)
                db = SessionLocal()
                try:
                    self._increment_usage(db, model_name, input_chars, output_chars)
                finally:
                    db.close()

                return f"[{model_name}] {ai_response}"

        except Exception as e:
            error_msg = str(e)
            if "503" in error_msg:
                return f"The {model_name} model is currently unavailable (service overloaded). Please try a different model or use Smart Routing for automatic fallback."
            elif "429" in error_msg:
                return f"Rate limit reached for {model_name}. Please try a different model or wait a few minutes."
            else:
                return f"Sorry, model {model_name} failed: {error_msg}"

    async def _chat_with_specific_gemini_model(self, message: str, project_context: str, chat_history: str, model_name: str, image_data: Optional[str] = None) -> str:
        """Chat using a specific Gemini model with optional image support"""
        user_analysis = rag_service.analyze_user_request(message)

        # Enhanced system instruction for image analysis
        if image_data:
            system_instruction = """You are an expert crochet instructor and pattern designer. When analyzing images of crochet patterns, provide:

1. **Pattern Name**: A descriptive name for the pattern shown
2. **Pattern Notation**: The abbreviated crochet notation (e.g., "ch 4, 12 dc in ring, sl st to join")
3. **Detailed Instructions**: Step-by-step instructions in plain English with clear paragraph breaks between rounds/rows
4. **Difficulty Level**: beginner, intermediate, or advanced
5. **Materials**: Yarn weight, hook size, and other supplies needed
6. **Estimated Time**: How long to complete (if determinable)
7. **Special Notes**: Any unique techniques or tips

Format your instructions with:
- Clear paragraph breaks between each round/row
- Numbered rounds/rows (e.g., "Round 1:", "Round 2:")
- Double line breaks between sections
- Bullet points for materials lists

Be thorough, accurate, and encouraging. Focus on making the pattern easy to follow."""
        else:
            system_instruction = """You are a friendly, expert crochet instructor and pattern designer. Help users with:
- Crochet technique questions
- Pattern interpretation and clarification
- Troubleshooting common problems
- Yarn and hook recommendations
- Project planning and modifications
- Stitch counting and pattern adjustments

Format your responses with clear paragraph breaks for readability.

NOTE: Diagram generation is temporarily disabled. When users ask for visual diagrams or charts, politely explain that you can provide detailed written descriptions of patterns instead, including step-by-step instructions and stitch placement explanations.

Always be encouraging and provide practical, actionable advice."""

        context_info = ""
        if project_context:
            context_info += f"\nCURRENT PROJECT CONTEXT:\n{project_context}\n"
        if chat_history:
            context_info += f"\nPREVIOUS CONVERSATION:\n{chat_history}\n"

        if user_analysis['requests_diagram']:
            pattern_text = message if any(pe in message.lower() for pe in ['round', 'row', 'chain', 'dc', 'sc']) else ""
            if pattern_text:
                rag_enhancement = rag_service.enhance_pattern_context(pattern_text, message)
                context_info += f"\n{rag_enhancement}\n"

        user_prompt = f"{context_info}\nUSER QUESTION: {message}"

        try:
            client = self._get_client()
            if not client:
                return "Gemini client not configured"

            # Build contents array with text and images if provided
            if image_data:
                try:
                    image_list = json.loads(image_data)
                    # Create parts list with text and images
                    parts = [user_prompt]
                    for img_base64 in image_list:
                        # Gemini SDK expects Part objects with inline_data
                        img_bytes = base64.b64decode(img_base64)

                        # Detect MIME type from magic bytes
                        mime_type = self._detect_mime_type(img_bytes)

                        parts.append(types.Part.from_bytes(
                            data=img_bytes,
                            mime_type=mime_type
                        ))
                    contents = parts
                except (json.JSONDecodeError, base64.binascii.Error) as e:
                    print(f"Warning: Failed to parse image data: {e}")
                    contents = user_prompt
            else:
                contents = user_prompt

            response = client.models.generate_content(
                model=model_name,
                contents=contents,
                config={
                    "system_instruction": system_instruction,
                    "temperature": 0.7,
                }
            )

            ai_response = response.text

            # Track usage
            input_chars = len(system_instruction) + len(user_prompt)
            output_chars = len(ai_response)
            db = SessionLocal()
            try:
                self._increment_usage(db, model_name, input_chars, output_chars)
            finally:
                db.close()

            return f"[{model_name}] {ai_response}"

        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower():
                return f"Daily quota reached for {model_name}. Please try a different model or wait until tomorrow."
            else:
                return f"Sorry, model {model_name} failed: {error_msg}"

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

    def get_ai_provider_config(self) -> Dict[str, Any]:
        """Get current AI provider configuration"""
        return {
            "use_openrouter": self.use_openrouter_default,
            "current_provider": self._ai_provider_preference,
            "selected_model": self._selected_model,
            "available_models": list(self.ALL_AVAILABLE_MODELS.keys()),
            "model_priority_order": self._model_priority_order
        }

    def set_ai_model(self, model_name: Optional[str] = None, priority_order: Optional[list] = None) -> Dict[str, Any]:
        """
        Set AI model configuration
        Three modes:
        1. Single Model: model_name is set
        2. Smart Routing: model_name=None, priority_order=None (complexity-based selection)
        3. Fallback Chain: model_name=None, priority_order=[...] (try in order until success)

        Args:
            model_name: Specific model to use, or None for smart/fallback routing
            priority_order: Custom priority order for fallback chain, or None for smart routing
        """
        # Validate model if specified
        if model_name and model_name not in self.ALL_AVAILABLE_MODELS:
            return {
                "success": False,
                "message": f"Invalid model: {model_name}. Available models: {list(self.ALL_AVAILABLE_MODELS.keys())}"
            }

        # Set model selection
        self._selected_model = model_name

        # Handle three distinct modes
        if model_name:
            # Mode 1: Single Model
            model_info = self.ALL_AVAILABLE_MODELS[model_name]
            if model_info["provider"] == "openrouter":
                self._ai_provider_preference = "openrouter"
                self.use_openrouter_default = True
            elif model_info["provider"] == "gemini":
                self._ai_provider_preference = "gemini"
                self.use_openrouter_default = False
            mode_description = f"Single Model: {model_name}"
        elif priority_order:
            # Mode 3: Fallback Chain
            # Validate priority order
            for model in priority_order:
                if model not in self.ALL_AVAILABLE_MODELS:
                    return {
                        "success": False,
                        "message": f"Invalid model in priority order: {model}"
                    }
            self._model_priority_order = priority_order
            self._ai_provider_preference = "auto"
            mode_description = f"Fallback Chain ({len(priority_order)} models)"
        else:
            # Mode 2: Smart Routing (complexity-based)
            self._model_priority_order = []  # Clear priority order for smart routing
            self._ai_provider_preference = "auto"
            mode_description = "Smart Routing (Complexity-Based)"

        # Persist configuration to database
        self._save_config_to_db()

        return {
            "success": True,
            "message": f"AI model configuration updated. Mode: {mode_description}",
            "use_openrouter": self.use_openrouter_default,
            "current_provider": self._ai_provider_preference,
            "selected_model": self._selected_model,
            "model_priority_order": self._model_priority_order
        }

# Global instance
ai_service = AIService()
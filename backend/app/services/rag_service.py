"""
RAG (Retrieval-Augmented Generation) Service for Crochet Charts
Enhances AI responses with specialized crochet chart knowledge
"""

from typing import Dict, List, Optional
from app.data.crochet_chart_knowledge import (
    CROCHET_SYMBOLS, CHART_LAYOUT_RULES, PATTERN_TEMPLATES,
    PROFESSIONAL_FEATURES, COMMON_PATTERNS,
    get_pattern_type, get_chart_features_for_pattern, find_similar_patterns
)
import re

class CrochetRAGService:
    def __init__(self):
        self.knowledge_base = {
            'symbols': CROCHET_SYMBOLS,
            'layouts': CHART_LAYOUT_RULES,
            'templates': PATTERN_TEMPLATES,
            'features': PROFESSIONAL_FEATURES,
            'patterns': COMMON_PATTERNS
        }

    def enhance_pattern_context(self, pattern_text: str, user_message: str) -> str:
        """
        Enhance AI context with relevant crochet chart knowledge
        """
        pattern_type = get_pattern_type(pattern_text)
        chart_features = get_chart_features_for_pattern(pattern_type)
        similar_patterns = find_similar_patterns(pattern_text)

        context_enhancement = f"""
CROCHET CHART EXPERTISE CONTEXT:

Pattern Type Detected: {pattern_type}

PROFESSIONAL CHART STANDARDS:
- Use traditional crochet symbols (not simple rectangles)
- Single Crochet (sc): X symbol with crossed lines
- Double Crochet (dc): Vertical line with 2 horizontal crossbars
- Half Double Crochet (hdc): Vertical line with 1 horizontal crossbar
- Chain (ch): Oval/circle symbol

VISUAL REQUIREMENTS FOR {pattern_type.upper()} PATTERNS:
"""

        if pattern_type in ['circular', 'square']:
            context_enhancement += """
- CENTER-OUT CONSTRUCTION: Start with magic ring in center
- RADIAL GUIDELINES: Show dashed lines from center to outer edge
- DIRECTIONAL ARROWS: Curved arrows showing counterclockwise work direction
- CONCENTRIC ROUNDS: Each round forms a larger circle around the previous
- STITCH CONNECTIONS: Show how each stitch connects to previous round
- ROUND LABELS: Clear numbering for each round
- STITCH COUNTS: Display total stitches per round in parentheses

MAGIC RING SPECIFICS:
- Round 1 stitches should radiate from center point
- Use proper stitch symbols arranged in a circle
- Show the slip stitch join completing each round
"""
        else:
            context_enhancement += """
- ROW-BY-ROW CONSTRUCTION: Work back and forth in rows
- TURNING CHAINS: Show chain stitches at row beginnings
- DIRECTIONAL ARROWS: Straight arrows showing row direction changes
- ROW ALIGNMENT: Stitches should align vertically between rows
"""

        # Add similar pattern examples if found
        if similar_patterns:
            context_enhancement += "\nSIMILAR PATTERN REFERENCE:\n"
            for pattern in similar_patterns[:2]:  # Limit to 2 examples
                context_enhancement += f"- {pattern['name']}: {pattern['data'][0]}\n"

        # Add specific diagram requirements
        context_enhancement += """
DIAGRAM GENERATION REQUIREMENTS:
1. Use authentic crochet chart symbols (X for sc, T-with-lines for dc/hdc)
2. Show radial guidelines for circular patterns (dashed lines from center)
3. Add curved directional arrows showing work flow
4. Include proper round/row numbering and stitch counts
5. Create professional layout matching traditional crochet charts
6. Use appropriate colors: black for symbols, gray for guidelines, red for arrows

AVOID: Simple rectangles, basic circles, amateur-looking diagrams
GOAL: Professional crochet chart matching published pattern standards
"""

        return context_enhancement

    def get_symbol_requirements(self, stitch_type: str) -> Dict:
        """Get specific symbol requirements for a stitch type"""
        if stitch_type in self.knowledge_base['symbols']:
            return self.knowledge_base['symbols'][stitch_type]
        return self.knowledge_base['symbols']['single_crochet']  # default

    def get_layout_requirements(self, pattern_type: str) -> Dict:
        """Get layout requirements for pattern type"""
        if pattern_type in ['circular', 'square']:
            return self.knowledge_base['layouts']['circular_patterns']
        else:
            return self.knowledge_base['layouts']['rectangular_patterns']

    def analyze_user_request(self, message: str) -> Dict:
        """Analyze user message for chart-specific requirements"""
        message_lower = message.lower()

        analysis = {
            'requests_diagram': False,
            'diagram_keywords': [],
            'pattern_elements': [],
            'quality_indicators': [],
            'specific_requirements': [],
            'pattern_type': 'unknown',
            'is_granny_square': False
        }

        # Check for diagram requests
        diagram_keywords = ['diagram', 'chart', 'visual', 'picture', 'drawing', 'show me']
        found_keywords = [kw for kw in diagram_keywords if kw in message_lower]
        analysis['requests_diagram'] = len(found_keywords) > 0
        analysis['diagram_keywords'] = found_keywords

        # Check for pattern elements
        pattern_elements = ['round', 'row', 'magic ring', 'foundation', 'stitch', 'increase', 'decrease']
        analysis['pattern_elements'] = [pe for pe in pattern_elements if pe in message_lower]

        # Check for quality indicators
        quality_terms = ['professional', 'proper', 'traditional', 'standard', 'like chatgpt', 'accurate']
        analysis['quality_indicators'] = [qt for qt in quality_terms if qt in message_lower]

        # Check for specific requirements
        if 'radial' in message_lower or 'line' in message_lower:
            analysis['specific_requirements'].append('radial_lines')
        if 'arrow' in message_lower or 'direction' in message_lower:
            analysis['specific_requirements'].append('directional_arrows')
        if 'symbol' in message_lower:
            analysis['specific_requirements'].append('proper_symbols')

        # Detect granny square patterns
        granny_indicators = ['granny square', 'granny', 'square', 'corner', 'ch 1', 'ch 2',
                           '3 dc', 'chain 4', 'ch 4', 'foundation loop', 'slip knot']
        analysis['is_granny_square'] = any(indicator in message_lower for indicator in granny_indicators)

        if analysis['is_granny_square']:
            analysis['pattern_type'] = 'granny_square'

        return analysis

# Global instance
rag_service = CrochetRAGService()
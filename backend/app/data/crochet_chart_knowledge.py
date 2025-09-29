"""
Crochet Chart Knowledge Base for RAG System
Contains standard crochet chart symbols, patterns, and visualization rules
"""

# Standard International Crochet Chart Symbols
CROCHET_SYMBOLS = {
    'chain': {
        'symbol': '○',
        'svg_path': 'M 0,0 A 3,3 0 1,1 6,0 A 3,3 0 1,1 0,0',
        'description': 'Chain stitch - oval symbol',
        'height': 6,
        'width': 6
    },
    'slip_stitch': {
        'symbol': '•',
        'svg_path': 'M 0,0 A 2,2 0 1,1 4,0 A 2,2 0 1,1 0,0',
        'description': 'Slip stitch - small filled oval',
        'height': 4,
        'width': 4
    },
    'single_crochet': {
        'symbol': '×',
        'svg_path': 'M 0,0 L 6,8 M 6,0 L 0,8',
        'description': 'Single crochet - X symbol',
        'height': 8,
        'width': 6
    },
    'half_double_crochet': {
        'symbol': '╤',
        'svg_path': 'M 3,0 L 3,12 M 0,6 L 6,6',
        'description': 'Half double crochet - T with horizontal line',
        'height': 12,
        'width': 6
    },
    'double_crochet': {
        'symbol': '╫',
        'svg_path': 'M 3,0 L 3,16 M 0,5 L 6,5 M 0,11 L 6,11',
        'description': 'Double crochet - T with two horizontal lines',
        'height': 16,
        'width': 6
    },
    'treble_crochet': {
        'symbol': '╬',
        'svg_path': 'M 3,0 L 3,20 M 0,4 L 6,4 M 0,8 L 6,8 M 0,12 L 6,12',
        'description': 'Treble crochet - T with three horizontal lines',
        'height': 20,
        'width': 6
    }
}

# Chart Layout Rules
CHART_LAYOUT_RULES = {
    'circular_patterns': {
        'center_start': True,
        'work_direction': 'counterclockwise',
        'round_spacing': 30,  # pixels between rounds
        'stitch_spacing': 'even_distribution',
        'show_round_numbers': True,
        'show_stitch_counts': True,
        'connection_lines': True
    },
    'rectangular_patterns': {
        'row_direction': 'alternate',  # right-to-left, then left-to-right
        'row_spacing': 20,
        'stitch_spacing': 15,
        'show_row_numbers': True,
        'turning_chains': True
    }
}

# Pattern Recognition Templates
PATTERN_TEMPLATES = {
    'magic_ring_start': {
        'pattern': r'(?:magic ring|magic circle)',
        'characteristics': {
            'type': 'circular',
            'center_method': 'adjustable_ring',
            'typical_first_round': 6-12,
            'growth_pattern': 'increase_each_round'
        }
    },
    'foundation_chain': {
        'pattern': r'(?:foundation|base|starting)\s+(?:chain|ch)',
        'characteristics': {
            'type': 'rectangular',
            'start_method': 'chain',
            'work_direction': 'back_and_forth'
        }
    },
    'granny_square': {
        'pattern': r'granny\s+square',
        'characteristics': {
            'type': 'square',
            'corner_increases': True,
            'cluster_stitches': True,
            'chain_spaces': True
        }
    }
}

# Professional Chart Features
PROFESSIONAL_FEATURES = {
    'radial_guidelines': {
        'show_for_circular': True,
        'line_style': 'dashed',
        'opacity': 0.3,
        'color': '#666666'
    },
    'directional_arrows': {
        'show_work_direction': True,
        'curved_for_circular': True,
        'straight_for_rows': True,
        'color': '#ff6b6b'
    },
    'stitch_connections': {
        'show_yarn_path': True,
        'connect_adjacent_stitches': True,
        'highlight_increases': True,
        'highlight_decreases': True
    },
    'annotations': {
        'round_labels': True,
        'stitch_counts': True,
        'special_instructions': True,
        'legend': True
    }
}

# Common Crochet Pattern Structures
COMMON_PATTERNS = {
    'basic_amigurumi_sphere': [
        "Round 1: 6 sc in magic ring",
        "Round 2: inc in each st around (12)",
        "Round 3: *sc, inc* repeat around (18)",
        "Round 4: *2 sc, inc* repeat around (24)",
        "Round 5: *3 sc, inc* repeat around (30)",
        "Round 6: *4 sc, inc* repeat around (36)"
    ],
    'granny_square_basic': [
        "Round 1: ch 4, join to form ring, ch 3 (counts as dc), 2 dc in ring, ch 2, *3 dc, ch 2* 3 times, join",
        "Round 2: ch 3, 2 dc in same sp, ch 1, *(3 dc, ch 2, 3 dc) in corner, ch 1* repeat around",
        "Round 3: ch 3, 2 dc in same sp, ch 1, 3 dc in next sp, ch 1, *(3 dc, ch 2, 3 dc) in corner, ch 1, 3 dc in next sp, ch 1* repeat around"
    ],
    'basic_scarf': [
        "Foundation: Ch 25",
        "Row 1: sc in 2nd ch from hook, sc across (24 sc)",
        "Row 2: ch 1, turn, sc in each st across",
        "Repeat Row 2 until desired length"
    ]
}

def get_pattern_type(pattern_text: str) -> str:
    """Determine pattern type from text"""
    text_lower = pattern_text.lower()

    if any(keyword in text_lower for keyword in ['magic ring', 'magic circle']):
        return 'circular'
    elif 'granny square' in text_lower:
        return 'square'
    elif any(keyword in text_lower for keyword in ['foundation', 'base chain', 'ch and turn']):
        return 'rectangular'
    elif 'round' in text_lower:
        return 'circular'
    elif 'row' in text_lower:
        return 'rectangular'
    else:
        return 'unknown'

def get_chart_features_for_pattern(pattern_type: str) -> dict:
    """Get appropriate chart features based on pattern type"""
    if pattern_type in ['circular', 'square']:
        return {
            'layout': CHART_LAYOUT_RULES['circular_patterns'],
            'symbols': CROCHET_SYMBOLS,
            'features': PROFESSIONAL_FEATURES
        }
    elif pattern_type == 'rectangular':
        return {
            'layout': CHART_LAYOUT_RULES['rectangular_patterns'],
            'symbols': CROCHET_SYMBOLS,
            'features': PROFESSIONAL_FEATURES
        }
    else:
        return {
            'layout': CHART_LAYOUT_RULES['circular_patterns'],
            'symbols': CROCHET_SYMBOLS,
            'features': PROFESSIONAL_FEATURES
        }

def find_similar_patterns(pattern_text: str) -> list:
    """Find similar patterns in knowledge base for reference"""
    text_lower = pattern_text.lower()
    similar = []

    for pattern_name, pattern_data in COMMON_PATTERNS.items():
        if any(keyword in text_lower for keyword in pattern_name.split('_')):
            similar.append({
                'name': pattern_name,
                'data': pattern_data,
                'relevance': 'high'
            })

    return similar
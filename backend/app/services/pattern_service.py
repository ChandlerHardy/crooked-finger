import re
import io
import base64
import math
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image, ImageDraw, ImageFont
import svgwrite
from app.data.crochet_chart_knowledge import get_pattern_type, get_chart_features_for_pattern

class PatternService:
    def __init__(self):
        self.stitch_symbols = {
            'sc': '×',
            'dc': '╫',
            'hdc': '╤',
            'tc': '╬',
            'sl st': '•',
            'ch': 'o',
            'inc': '▲',
            'dec': '▼',
            'yo': '○',
            'sk': '—'
        }

    def parse_pattern_structure(self, pattern_text: str) -> Dict:
        """
        Parse crochet pattern to extract structure information
        """
        lines = pattern_text.strip().split('\n')
        rounds = []
        current_round = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if this line starts a new round
            round_match = re.match(r'(?:round|rnd|row)\s*(\d+)', line.lower())
            if round_match:
                if current_round:
                    rounds.append(current_round)
                current_round = {
                    'number': int(round_match.group(1)),
                    'instructions': line,
                    'stitches': self._count_stitches(line),
                    'stitch_types': self._identify_stitch_types(line)
                }
            elif current_round:
                current_round['instructions'] += ' ' + line
                current_round['stitches'] += self._count_stitches(line)
                current_round['stitch_types'].update(self._identify_stitch_types(line))

        if current_round:
            rounds.append(current_round)

        return {
            'total_rounds': len(rounds),
            'rounds': rounds,
            'pattern_type': self._determine_pattern_type(pattern_text),
            'estimated_size': self._estimate_size(rounds),
            'pattern_text': pattern_text  # Include original text for RAG
        }

    def generate_stitch_diagram_svg(self, pattern_data: Dict) -> str:
        """
        Generate a professional crochet chart with proper symbols, radial lines, and directional arrows
        """
        pattern_type = get_pattern_type(pattern_data.get('pattern_text', ''))
        chart_features = get_chart_features_for_pattern(pattern_type)

        max_stitches = max([r['stitches'] for r in pattern_data['rounds']] + [12])
        width = min(600, max(400, max_stitches * 20))
        height = 500

        dwg = svgwrite.Drawing(size=(width, height))

        # Add clean white background
        dwg.add(dwg.rect(insert=(0, 0), size=(width, height), fill='white'))

        # Add title
        dwg.add(dwg.text('Crochet Pattern Chart',
                        insert=(width//2, 25),
                        text_anchor='middle',
                        font_size='16px',
                        font_weight='bold',
                        fill='#1f2937'))

        # Pattern info
        dwg.add(dwg.text(f"Pattern: {pattern_data['pattern_type']} • {pattern_data['total_rounds']} rounds",
                        insert=(width//2, 45),
                        text_anchor='middle',
                        font_size='11px',
                        fill='#6b7280'))

        center_x = width // 2
        center_y = height // 2 + 20  # Move down slightly for better layout

        # Draw radial guidelines first (behind everything)
        if pattern_type in ['circular', 'square']:
            self._draw_radial_guidelines(dwg, center_x, center_y, pattern_data['rounds'])

        # Draw directional arrow for work flow
        self._draw_directional_arrows(dwg, center_x, center_y, pattern_data['rounds'], pattern_type)

        # Draw concentric rounds with professional stitch symbols
        for round_data in pattern_data['rounds']:
            round_num = round_data['number']
            stitch_count = round_data['stitches']

            # Calculate radius for this round
            radius = 50 + (round_num - 1) * 35

            # Draw round guidelines (light circles)
            dwg.add(dwg.circle(center=(center_x, center_y), r=radius,
                             fill='none', stroke='#e5e7eb', stroke_width='0.5', opacity='0.3'))

            # Round label with stitch count
            label_x = center_x - radius - 50
            dwg.add(dwg.text(f"R{round_num}",
                           insert=(label_x, center_y - radius + 8),
                           font_size='11px',
                           font_weight='bold',
                           fill='#374151'))

            dwg.add(dwg.text(f"({stitch_count})",
                           insert=(label_x, center_y - radius + 22),
                           font_size='9px',
                           fill='#6b7280'))

            # Draw professional stitch symbols
            if stitch_count > 0:
                self._draw_round_stitches(dwg, center_x, center_y, radius, round_data)

        # Add professional legend
        self._draw_professional_legend(dwg, width, height)

        return dwg.tostring()

    def _draw_radial_guidelines(self, dwg, center_x, center_y, rounds):
        """Draw radial guidelines from center to outer edge"""
        if not rounds:
            return

        max_radius = 50 + (len(rounds) - 1) * 35

        # Draw 8 radial lines for main compass points
        for i in range(8):
            angle = i * 45  # 45-degree intervals
            end_x = center_x + max_radius * math.cos(math.radians(angle - 90))
            end_y = center_y + max_radius * math.sin(math.radians(angle - 90))

            dwg.add(dwg.line(start=(center_x, center_y), end=(end_x, end_y),
                           stroke='#d1d5db', stroke_width='0.5',
                           stroke_dasharray='3,3', opacity='0.4'))

    def _draw_directional_arrows(self, dwg, center_x, center_y, rounds, pattern_type):
        """Draw curved arrows showing work direction"""
        if not rounds or pattern_type not in ['circular', 'square']:
            return

        # Draw curved arrow around the outermost round
        if len(rounds) > 1:
            outer_radius = 50 + (len(rounds) - 1) * 35 + 15

            # Create curved arrow path (counterclockwise)
            start_angle = -60  # Start at top-right
            end_angle = start_angle + 270  # 3/4 circle

            # Create SVG path for curved arrow
            large_arc = 1 if abs(end_angle - start_angle) > 180 else 0

            start_x = center_x + outer_radius * math.cos(math.radians(start_angle))
            start_y = center_y + outer_radius * math.sin(math.radians(start_angle))
            end_x = center_x + outer_radius * math.cos(math.radians(end_angle))
            end_y = center_y + outer_radius * math.sin(math.radians(end_angle))

            path_data = f"M {start_x},{start_y} A {outer_radius},{outer_radius} 0 {large_arc},0 {end_x},{end_y}"

            dwg.add(dwg.path(d=path_data, stroke='#ef4444', stroke_width='2',
                           fill='none', marker_end='url(#arrowhead)'))

            # Define arrowhead marker
            marker = dwg.defs.add(dwg.marker(insert=(5, 3), size=(10, 6), orient='auto'))
            marker['id'] = 'arrowhead'
            marker.add(dwg.path(d='M 0,0 L 0,6 L 9,3 z', fill='#ef4444'))

    def _draw_round_stitches(self, dwg, center_x, center_y, radius, round_data):
        """Draw professional stitch symbols around a round"""
        stitch_count = round_data['stitches']
        stitch_types = round_data['stitch_types']

        if stitch_count == 0:
            return

        angle_step = 360 / stitch_count

        for i in range(stitch_count):
            angle = i * angle_step - 90  # Start at top
            x = center_x + radius * math.cos(math.radians(angle))
            y = center_y + radius * math.sin(math.radians(angle))

            # Determine stitch type for this position
            dominant_stitch = self._get_dominant_stitch_type(stitch_types)

            # Draw professional stitch symbol
            self._draw_stitch_symbol(dwg, x, y, dominant_stitch, angle)

    def _draw_stitch_symbol(self, dwg, x, y, stitch_type, angle):
        """Draw a professional crochet stitch symbol"""
        # Colors for different stitch types
        colors = {
            'sc': '#000000',  # Black for single crochet
            'dc': '#000000',  # Black for double crochet
            'hdc': '#000000', # Black for half double crochet
            'ch': '#666666',  # Gray for chains
            'sl st': '#333333'  # Dark gray for slip stitches
        }

        color = colors.get(stitch_type, '#000000')

        if stitch_type == 'sc':
            # Single crochet: X symbol
            size = 4
            dwg.add(dwg.line(start=(x-size, y-size), end=(x+size, y+size),
                           stroke=color, stroke_width='1.5'))
            dwg.add(dwg.line(start=(x-size, y+size), end=(x+size, y-size),
                           stroke=color, stroke_width='1.5'))

        elif stitch_type == 'dc':
            # Double crochet: Vertical line with 2 horizontal bars
            height = 12
            dwg.add(dwg.line(start=(x, y-height//2), end=(x, y+height//2),
                           stroke=color, stroke_width='2'))
            # Two horizontal bars
            bar_width = 4
            dwg.add(dwg.line(start=(x-bar_width, y-height//4), end=(x+bar_width, y-height//4),
                           stroke=color, stroke_width='1.5'))
            dwg.add(dwg.line(start=(x-bar_width, y+height//4), end=(x+bar_width, y+height//4),
                           stroke=color, stroke_width='1.5'))

        elif stitch_type == 'hdc':
            # Half double crochet: Vertical line with 1 horizontal bar
            height = 10
            dwg.add(dwg.line(start=(x, y-height//2), end=(x, y+height//2),
                           stroke=color, stroke_width='2'))
            # One horizontal bar
            bar_width = 4
            dwg.add(dwg.line(start=(x-bar_width, y), end=(x+bar_width, y),
                           stroke=color, stroke_width='1.5'))

        elif stitch_type == 'ch':
            # Chain: Small oval
            dwg.add(dwg.ellipse(center=(x, y), r=(3, 2),
                              fill='none', stroke=color, stroke_width='1.5'))

        elif stitch_type == 'sl st':
            # Slip stitch: Small filled circle
            dwg.add(dwg.circle(center=(x, y), r=2,
                             fill=color))

        else:
            # Default: Single crochet X
            size = 4
            dwg.add(dwg.line(start=(x-size, y-size), end=(x+size, y+size),
                           stroke=color, stroke_width='1.5'))
            dwg.add(dwg.line(start=(x-size, y+size), end=(x+size, y-size),
                           stroke=color, stroke_width='1.5'))

    def _draw_professional_legend(self, dwg, width, height):
        """Draw a professional legend with proper symbols"""
        legend_y = height - 120
        legend_x = 30

        # Legend title
        dwg.add(dwg.text('Chart Symbols:',
                        insert=(legend_x, legend_y),
                        font_size='12px',
                        font_weight='bold',
                        fill='#1f2937'))

        # Legend items with actual symbols
        legend_items = [
            ('X', 'Single Crochet (sc)'),
            ('T with 1 bar', 'Half Double Crochet (hdc)'),
            ('T with 2 bars', 'Double Crochet (dc)'),
            ('○', 'Chain (ch)'),
            ('•', 'Slip Stitch (sl st)')
        ]

        y_offset = legend_y + 20
        for i, (symbol, description) in enumerate(legend_items):
            y = y_offset + (i * 18)

            # Draw symbol example
            if symbol == 'X':
                self._draw_stitch_symbol(dwg, legend_x + 10, y, 'sc', 0)
            elif 'T with 1 bar' in symbol:
                self._draw_stitch_symbol(dwg, legend_x + 10, y, 'hdc', 0)
            elif 'T with 2 bars' in symbol:
                self._draw_stitch_symbol(dwg, legend_x + 10, y, 'dc', 0)
            elif symbol == '○':
                self._draw_stitch_symbol(dwg, legend_x + 10, y, 'ch', 0)
            elif symbol == '•':
                self._draw_stitch_symbol(dwg, legend_x + 10, y, 'sl st', 0)

            # Label
            dwg.add(dwg.text(description,
                           insert=(legend_x + 25, y + 4),
                           font_size='10px',
                           fill='#374151'))

    def _get_dominant_stitch_type(self, stitch_types: Dict[str, int]) -> str:
        """Get the most common stitch type in a round"""
        if not stitch_types:
            return 'sc'  # default
        return max(stitch_types.items(), key=lambda x: x[1])[0]

    def generate_pattern_chart_png(self, pattern_data: Dict) -> str:
        """
        Generate PNG pattern chart using matplotlib
        """
        fig, ax = plt.subplots(figsize=(10, 8))

        # Create visual representation of rounds
        rounds = pattern_data['rounds']
        if not rounds:
            ax.text(0.5, 0.5, 'No pattern data available',
                   ha='center', va='center', transform=ax.transAxes)
        else:
            # Draw concentric circles for rounds (for circular patterns)
            center_x, center_y = 0.5, 0.5
            max_radius = 0.4

            for i, round_data in enumerate(rounds):
                radius = (i + 1) / len(rounds) * max_radius
                circle = patches.Circle((center_x, center_y), radius,
                                      fill=False, linestyle='-', linewidth=2)
                ax.add_patch(circle)

                # Add round label
                label_x = center_x + radius + 0.05
                ax.text(label_x, center_y, f"R{round_data['number']} ({round_data['stitches']})",
                       va='center', fontsize=10)

        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_aspect('equal')
        ax.set_title('Pattern Chart', fontsize=14, fontweight='bold')
        ax.axis('off')

        # Save to base64 string
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()

        return image_base64

    def _count_stitches(self, instruction: str) -> int:
        """Count total stitches in an instruction"""
        instruction_lower = instruction.lower()

        # Look for explicit total stitch count in parentheses first (most reliable)
        explicit_total = re.search(r'\((\d+)\s*(?:dc|sc|hdc|tc|sts?|stitches?)\)', instruction_lower)
        if explicit_total:
            return int(explicit_total.group(1))

        # Look for total pattern at end
        total_pattern = re.search(r'total.*?(\d+)', instruction_lower)
        if total_pattern:
            return int(total_pattern.group(1))

        # For magic ring patterns: "11 dc in magic ring" = 11 + ch 3 = 12 total
        magic_ring_pattern = re.search(r'(\d+)\s+(?:dc|sc|hdc|tc)\s+(?:in|into)\s+magic\s+ring', instruction_lower)
        if magic_ring_pattern:
            base_count = int(magic_ring_pattern.group(1))
            # Add 1 for starting chain that counts as first stitch
            if 'ch 3' in instruction_lower or 'chain 3' in instruction_lower:
                return base_count + 1
            return base_count

        # For increase patterns: "2 dc in each st around" - look for multiplier
        increase_pattern = re.search(r'(\d+)\s+(?:dc|sc|hdc|tc)\s+in\s+each', instruction_lower)
        if increase_pattern:
            multiplier = int(increase_pattern.group(1))
            # Try to find previous round count or estimate
            prev_count = re.search(r'from.*?(\d+)', instruction_lower)
            if prev_count:
                return multiplier * int(prev_count.group(1))
            # If we find "12 stitches from Round 1" pattern
            prev_round = re.search(r'(\d+)\s+(?:sts?|stitches?)', instruction_lower)
            if prev_round:
                return multiplier * int(prev_round.group(1))

        # Count individual stitches as fallback
        stitch_count = 0
        stitch_patterns = [
            r'(\d+)\s*dc(?!\s*in\s*each)',  # "11 dc" but not "2 dc in each"
            r'(\d+)\s*sc(?!\s*in\s*each)',
            r'(\d+)\s*hdc(?!\s*in\s*each)',
            r'(\d+)\s*tc(?!\s*in\s*each)'
        ]

        for pattern in stitch_patterns:
            matches = re.findall(pattern, instruction_lower)
            for match in matches:
                stitch_count += int(match)

        # Add 1 for chain 3 that counts as dc
        if 'ch 3' in instruction_lower and stitch_count > 0:
            stitch_count += 1

        return max(stitch_count, 1)

    def _identify_stitch_types(self, instruction: str) -> Dict[str, int]:
        """Identify and count different stitch types"""
        stitch_types = {}
        instruction_lower = instruction.lower()

        for abbrev in self.stitch_symbols.keys():
            pattern = r'\b' + re.escape(abbrev) + r'\b'
            count = len(re.findall(pattern, instruction_lower))
            if count > 0:
                stitch_types[abbrev] = count

        return stitch_types

    def _determine_pattern_type(self, pattern_text: str) -> str:
        """Determine if pattern is worked in rounds, rows, or other"""
        text_lower = pattern_text.lower()

        if 'magic ring' in text_lower or 'magic circle' in text_lower:
            return 'circular'
        elif re.search(r'\b(?:round|rnd)\b', text_lower):
            return 'rounds'
        elif re.search(r'\brow\b', text_lower):
            return 'rows'
        else:
            return 'unknown'

    def _estimate_size(self, rounds: List[Dict]) -> str:
        """Estimate finished size based on stitch counts"""
        if not rounds:
            return "unknown"

        total_stitches = sum(r['stitches'] for r in rounds)
        if total_stitches < 50:
            return "small (< 3 inches)"
        elif total_stitches < 200:
            return "medium (3-6 inches)"
        else:
            return "large (> 6 inches)"

    def _get_dominant_stitch_symbol(self, stitch_types: Dict[str, int]) -> str:
        """Get the symbol for the most common stitch type"""
        if not stitch_types:
            return '×'  # default to single crochet symbol

        dominant_stitch = max(stitch_types.items(), key=lambda x: x[1])[0]
        return self.stitch_symbols.get(dominant_stitch, '×')

# Global instance
pattern_service = PatternService()
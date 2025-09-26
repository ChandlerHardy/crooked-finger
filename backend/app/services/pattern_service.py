import re
import io
import base64
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image, ImageDraw, ImageFont
import svgwrite

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
            'estimated_size': self._estimate_size(rounds)
        }

    def generate_stitch_diagram_svg(self, pattern_data: Dict) -> str:
        """
        Generate SVG stitch diagram from pattern data
        """
        width = 400
        height = max(400, len(pattern_data['rounds']) * 30 + 100)

        dwg = svgwrite.Drawing(size=(width, height))

        # Add title
        dwg.add(dwg.text('Stitch Diagram',
                        insert=(width//2, 30),
                        text_anchor='middle',
                        font_size='16px',
                        font_weight='bold'))

        y_pos = 60
        for round_data in pattern_data['rounds']:
            round_num = round_data['number']
            stitch_count = round_data['stitches']

            # Round label
            dwg.add(dwg.text(f"Round {round_num}: {stitch_count} stitches",
                           insert=(20, y_pos),
                           font_size='12px'))

            # Draw stitch symbols
            x_start = 50
            symbol_spacing = min(300 / max(stitch_count, 1), 20)

            for i in range(min(stitch_count, 15)):  # Limit display for readability
                symbol = self._get_dominant_stitch_symbol(round_data['stitch_types'])
                dwg.add(dwg.text(symbol,
                               insert=(x_start + i * symbol_spacing, y_pos + 20),
                               font_size='14px',
                               text_anchor='middle'))

            if stitch_count > 15:
                dwg.add(dwg.text('...',
                               insert=(x_start + 15 * symbol_spacing, y_pos + 20),
                               font_size='14px'))

            y_pos += 50

        # Add legend
        legend_y = y_pos + 20
        dwg.add(dwg.text('Legend:', insert=(20, legend_y), font_size='12px', font_weight='bold'))
        legend_y += 20

        for stitch, symbol in self.stitch_symbols.items():
            dwg.add(dwg.text(f"{symbol} = {stitch}",
                           insert=(30, legend_y),
                           font_size='10px'))
            legend_y += 15

        return dwg.tostring()

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
        # Look for explicit stitch counts
        count_patterns = [
            r'(\d+)\s*(?:sc|dc|hdc|tc|sl st|ch)',
            r'(?:sc|dc|hdc|tc|sl st|ch)\s*(\d+)',
            r'(\d+)\s*times?',
            r'total.*?(\d+)',
            r'\((\d+)\s*(?:sts?|stitches?)\)'
        ]

        total = 0
        for pattern in count_patterns:
            matches = re.findall(pattern, instruction.lower())
            for match in matches:
                try:
                    total += int(match)
                except ValueError:
                    continue

        # If no explicit count found, estimate based on stitch abbreviations
        if total == 0:
            stitch_abbrevs = ['sc', 'dc', 'hdc', 'tc', 'sl st', 'ch']
            for abbrev in stitch_abbrevs:
                total += len(re.findall(r'\b' + abbrev + r'\b', instruction.lower()))

        return max(total, 1)  # At least 1 stitch

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
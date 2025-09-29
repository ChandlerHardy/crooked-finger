"""
Specialized Granny Square Chart Generator
Creates professional crochet charts specifically for granny square patterns
"""

import svgwrite
import math
from typing import Dict, List, Tuple

class GrannySquareService:
    def __init__(self):
        # Professional granny square chart dimensions
        self.width = 600
        self.height = 600
        self.center_x = self.width // 2
        self.center_y = self.height // 2

        # Colors matching professional charts
        self.colors = {
            'background': '#ffffff',
            'symbols': '#000000',
            'chains': '#000000',
            'guidelines': '#cccccc',
            'text': '#000000'
        }

    def generate_granny_square_chart(self, rounds: int = 3) -> str:
        """
        Generate a professional granny square chart like Image #5
        """
        dwg = svgwrite.Drawing(size=(self.width, self.height))

        # Add white background
        dwg.add(dwg.rect(insert=(0, 0), size=(self.width, self.height),
                        fill=self.colors['background']))

        # Add title
        dwg.add(dwg.text('Granny Square Pattern Chart',
                        insert=(self.center_x, 40),
                        text_anchor='middle',
                        font_size='18px',
                        font_weight='bold',
                        fill=self.colors['text']))

        # Starting chain ring in center
        self._draw_foundation_ring(dwg)

        # Draw each round
        for round_num in range(1, rounds + 1):
            self._draw_granny_round(dwg, round_num)

        # Add legend
        self._draw_granny_legend(dwg)

        return dwg.tostring()

    def _draw_foundation_ring(self, dwg):
        """Draw the foundation chain-4 ring in center"""
        ring_radius = 15

        # Draw the chain ring as connected ovals
        for i in range(4):
            angle = i * 90
            x = self.center_x + (ring_radius * 0.7) * math.cos(math.radians(angle))
            y = self.center_y + (ring_radius * 0.7) * math.sin(math.radians(angle))

            # Chain oval
            dwg.add(dwg.ellipse(center=(x, y), r=(4, 6),
                              fill='none', stroke=self.colors['chains'],
                              stroke_width='2'))

    def _draw_granny_round(self, dwg, round_num: int):
        """Draw a specific round of the granny square"""
        if round_num == 1:
            self._draw_round_1(dwg)
        elif round_num == 2:
            self._draw_round_2(dwg)
        elif round_num == 3:
            self._draw_round_3(dwg)

    def _draw_round_1(self, dwg):
        """
        Round 1: ch 3, 2 dc, ch 1, [3 dc, ch 1] 3 times, join
        Creates 4 corner groups of 3 dc each
        """
        radius = 60

        # Four corners at 45, 135, 225, 315 degrees
        corner_angles = [45, 135, 225, 315]

        for i, angle in enumerate(corner_angles):
            # Calculate corner position
            corner_x = self.center_x + radius * math.cos(math.radians(angle))
            corner_y = self.center_y + radius * math.sin(math.radians(angle))

            # Draw 3 dc cluster
            self._draw_dc_cluster(dwg, corner_x, corner_y, angle, 3)

            # Draw corner chain space
            self._draw_corner_chain_space(dwg, corner_x, corner_y, angle)

    def _draw_round_2(self, dwg):
        """
        Round 2: [3 dc, ch 2, 3 dc] in each corner space
        """
        radius = 100
        corner_angles = [45, 135, 225, 315]

        for i, angle in enumerate(corner_angles):
            corner_x = self.center_x + radius * math.cos(math.radians(angle))
            corner_y = self.center_y + radius * math.sin(math.radians(angle))

            # Draw corner: 3 dc, ch 2, 3 dc
            self._draw_corner_group(dwg, corner_x, corner_y, angle)

    def _draw_round_3(self, dwg):
        """
        Round 3: Corner groups + side groups
        """
        radius = 140

        # Corners
        corner_angles = [45, 135, 225, 315]
        for angle in corner_angles:
            corner_x = self.center_x + radius * math.cos(math.radians(angle))
            corner_y = self.center_y + radius * math.sin(math.radians(angle))
            self._draw_corner_group(dwg, corner_x, corner_y, angle)

        # Sides
        side_angles = [0, 90, 180, 270]
        side_radius = radius * 0.85
        for angle in side_angles:
            side_x = self.center_x + side_radius * math.cos(math.radians(angle))
            side_y = self.center_y + side_radius * math.sin(math.radians(angle))
            self._draw_dc_cluster(dwg, side_x, side_y, angle, 3)

    def _draw_dc_cluster(self, dwg, x: float, y: float, angle: float, count: int):
        """Draw a cluster of double crochet stitches with proper grouping"""
        spacing = 10
        start_offset = -(count - 1) * spacing / 2

        # Draw cluster base connection (showing stitches worked into same space)
        if count > 1:
            cluster_base_x = x - 15 * math.cos(math.radians(angle))
            cluster_base_y = y - 15 * math.sin(math.radians(angle))

            # Draw base point where all stitches connect
            dwg.add(dwg.circle(center=(cluster_base_x, cluster_base_y), r=2,
                             fill=self.colors['symbols']))

        for i in range(count):
            # Calculate position for each dc
            offset = start_offset + i * spacing

            # Rotate offset based on angle (perpendicular to radial direction)
            dc_x = x + offset * math.cos(math.radians(angle + 90))
            dc_y = y + offset * math.sin(math.radians(angle + 90))

            # Draw double crochet symbol (T with two bars)
            self._draw_dc_symbol(dwg, dc_x, dc_y, angle)

            # Draw connection line from each stitch to cluster base
            if count > 1:
                cluster_base_x = x - 15 * math.cos(math.radians(angle))
                cluster_base_y = y - 15 * math.sin(math.radians(angle))

                dwg.add(dwg.line(start=(dc_x, dc_y), end=(cluster_base_x, cluster_base_y),
                               stroke=self.colors['symbols'],
                               stroke_width='1',
                               opacity='0.6'))

    def _draw_dc_symbol(self, dwg, x: float, y: float, angle: float):
        """Draw a professional double crochet symbol with proper orientation"""
        height = 20
        bar_width = 6

        # Calculate rotated positions based on angle
        # For granny squares, stitches should be oriented radially from center
        rad_angle = math.radians(angle)

        # Vertical line (oriented toward center)
        half_height = height / 2
        start_x = x - half_height * math.cos(rad_angle)
        start_y = y - half_height * math.sin(rad_angle)
        end_x = x + half_height * math.cos(rad_angle)
        end_y = y + half_height * math.sin(rad_angle)

        dwg.add(dwg.line(start=(start_x, start_y), end=(end_x, end_y),
                        stroke=self.colors['symbols'], stroke_width='2'))

        # Two horizontal bars (perpendicular to the main line)
        bar_half_width = bar_width / 2
        for bar_offset in [-6, 6]:
            # Calculate bar position along the main line
            bar_center_x = x + bar_offset * math.cos(rad_angle)
            bar_center_y = y + bar_offset * math.sin(rad_angle)

            # Calculate bar endpoints (perpendicular to main line)
            bar_start_x = bar_center_x - bar_half_width * math.cos(rad_angle + math.pi/2)
            bar_start_y = bar_center_y - bar_half_width * math.sin(rad_angle + math.pi/2)
            bar_end_x = bar_center_x + bar_half_width * math.cos(rad_angle + math.pi/2)
            bar_end_y = bar_center_y + bar_half_width * math.sin(rad_angle + math.pi/2)

            dwg.add(dwg.line(start=(bar_start_x, bar_start_y), end=(bar_end_x, bar_end_y),
                           stroke=self.colors['symbols'], stroke_width='1.5'))

        # Draw connection line to center (showing stitch base)
        self._draw_connection_line(dwg, x, y, angle)

    def _draw_connection_line(self, dwg, x: float, y: float, angle: float):
        """Draw connection line from stitch to center/previous round"""
        # Calculate connection line toward center
        connection_length = 25
        rad_angle = math.radians(angle)

        # Line from stitch base toward center
        end_x = x - connection_length * math.cos(rad_angle)
        end_y = y - connection_length * math.sin(rad_angle)

        dwg.add(dwg.line(start=(x, y), end=(end_x, end_y),
                        stroke=self.colors['guidelines'],
                        stroke_width='1',
                        stroke_dasharray='2,1',
                        opacity='0.7'))

    def _draw_corner_chain_space(self, dwg, x: float, y: float, angle: float):
        """Draw a corner chain space"""
        # Draw chain oval for corner space
        chain_x = x + 15 * math.cos(math.radians(angle + 45))
        chain_y = y + 15 * math.sin(math.radians(angle + 45))

        dwg.add(dwg.ellipse(center=(chain_x, chain_y), r=(3, 5),
                          fill='none', stroke=self.colors['chains'],
                          stroke_width='1.5'))

    def _draw_corner_group(self, dwg, x: float, y: float, angle: float):
        """Draw a corner group: 3 dc, ch 2, 3 dc"""
        # Calculate positions for corner groups
        group_spacing = 18
        cluster1_x = x - group_spacing * math.cos(math.radians(angle))
        cluster1_y = y - group_spacing * math.sin(math.radians(angle))
        cluster2_x = x + group_spacing * math.cos(math.radians(angle))
        cluster2_y = y + group_spacing * math.sin(math.radians(angle))

        # First 3 dc group
        self._draw_dc_cluster(dwg, cluster1_x, cluster1_y, angle - 15, 3)

        # Corner chain space (ch 2) - positioned prominently
        chain_x = x + 8 * math.cos(math.radians(angle + 90))
        chain_y = y + 8 * math.sin(math.radians(angle + 90))

        # Draw two chain symbols for ch 2
        dwg.add(dwg.ellipse(center=(chain_x - 3, chain_y), r=(3, 4),
                          fill='none', stroke=self.colors['chains'],
                          stroke_width='1.5'))
        dwg.add(dwg.ellipse(center=(chain_x + 3, chain_y), r=(3, 4),
                          fill='none', stroke=self.colors['chains'],
                          stroke_width='1.5'))

        # Draw connection lines from clusters to chain space
        dwg.add(dwg.line(start=(cluster1_x, cluster1_y), end=(chain_x, chain_y),
                        stroke=self.colors['guidelines'],
                        stroke_width='1',
                        stroke_dasharray='1,1',
                        opacity='0.5'))
        dwg.add(dwg.line(start=(cluster2_x, cluster2_y), end=(chain_x, chain_y),
                        stroke=self.colors['guidelines'],
                        stroke_width='1',
                        stroke_dasharray='1,1',
                        opacity='0.5'))

        # Second 3 dc group
        self._draw_dc_cluster(dwg, cluster2_x, cluster2_y, angle + 15, 3)

    def _draw_granny_legend(self, dwg):
        """Draw legend matching professional charts"""
        legend_x = 50
        legend_y = self.height - 120

        # Legend title
        dwg.add(dwg.text('Chart Symbols:',
                        insert=(legend_x, legend_y),
                        font_size='14px',
                        font_weight='bold',
                        fill=self.colors['text']))

        # Symbol examples
        symbols = [
            ('Double Crochet (dc)', 'dc'),
            ('Chain (ch)', 'chain'),
            ('Corner Space (ch-2)', 'corner'),
            ('Join with sl st', 'join')
        ]

        for i, (description, symbol_type) in enumerate(symbols):
            y = legend_y + 25 + (i * 20)

            # Draw symbol example
            if symbol_type == 'dc':
                self._draw_dc_symbol(dwg, legend_x + 15, y, 0)
            elif symbol_type == 'chain':
                dwg.add(dwg.ellipse(center=(legend_x + 15, y), r=(3, 5),
                                  fill='none', stroke=self.colors['chains'],
                                  stroke_width='1.5'))
            elif symbol_type == 'corner':
                dwg.add(dwg.ellipse(center=(legend_x + 15, y), r=(4, 6),
                                  fill='none', stroke=self.colors['chains'],
                                  stroke_width='2'))
            elif symbol_type == 'join':
                dwg.add(dwg.circle(center=(legend_x + 15, y), r=3,
                                 fill=self.colors['symbols']))

            # Description
            dwg.add(dwg.text(description,
                           insert=(legend_x + 35, y + 4),
                           font_size='11px',
                           fill=self.colors['text']))

# Global instance
granny_square_service = GrannySquareService()
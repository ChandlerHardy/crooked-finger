"""
Flowing Granny Square Chart Generator
Creates connected, flowing granny square charts like professional crochet diagrams
"""

import svgwrite
import math
from typing import Dict, List, Tuple

class FlowingGrannyService:
    def __init__(self):
        self.width = 500
        self.height = 500
        self.center_x = self.width // 2
        self.center_y = self.height // 2

        # Professional chart colors
        self.colors = {
            'background': '#ffffff',
            'symbols': '#000000',
            'connections': '#000000',
            'text': '#000000'
        }

    def generate_flowing_granny_chart(self) -> str:
        """
        Generate a flowing granny square chart matching professional standards
        """
        dwg = svgwrite.Drawing(size=(self.width, self.height))

        # Add white background
        dwg.add(dwg.rect(insert=(0, 0), size=(self.width, self.height),
                        fill=self.colors['background']))

        # Add title
        dwg.add(dwg.text('Granny Square Pattern Chart',
                        insert=(self.center_x, 30),
                        text_anchor='middle',
                        font_size='16px',
                        font_weight='bold',
                        fill=self.colors['text']))

        # Draw the square structure with flowing connections
        self._draw_center_ring(dwg)
        self._draw_round_1(dwg)
        self._draw_round_2(dwg)
        self._draw_flowing_connections(dwg)

        # Add legend
        self._draw_legend(dwg)

        return dwg.tostring()

    def _draw_center_ring(self, dwg):
        """Draw the foundation chain-4 ring in center"""
        # Draw a small ring of connected chains
        ring_radius = 8

        # Draw 4 connected chain ovals forming a ring
        for i in range(4):
            angle = i * 90
            x = self.center_x + ring_radius * math.cos(math.radians(angle))
            y = self.center_y + ring_radius * math.sin(math.radians(angle))

            # Chain oval
            dwg.add(dwg.ellipse(center=(x, y), r=(3, 5),
                              fill='none', stroke=self.colors['symbols'],
                              stroke_width='1.5'))

        # Add center connection point
        dwg.add(dwg.circle(center=(self.center_x, self.center_y), r=2,
                         fill=self.colors['symbols']))

    def _draw_round_1(self, dwg):
        """
        Round 1: 4 corners with 3 dc each, separated by ch 1 spaces
        """
        # Square corners at 45, 135, 225, 315 degrees
        corner_distance = 50
        corner_angles = [45, 135, 225, 315]

        for i, angle in enumerate(corner_angles):
            corner_x = self.center_x + corner_distance * math.cos(math.radians(angle))
            corner_y = self.center_y + corner_distance * math.sin(math.radians(angle))

            # Draw 3 dc cluster at corner
            self._draw_flowing_dc_cluster(dwg, corner_x, corner_y, angle, 3)

            # Draw ch 1 space between corners
            if i < len(corner_angles) - 1:
                next_angle = corner_angles[i + 1]
            else:
                next_angle = corner_angles[0]

            mid_angle = (angle + next_angle) / 2
            if mid_angle < angle:  # Handle wrap-around
                mid_angle += 180

            chain_x = self.center_x + (corner_distance * 0.7) * math.cos(math.radians(mid_angle))
            chain_y = self.center_y + (corner_distance * 0.7) * math.sin(math.radians(mid_angle))

            # Single chain oval for ch 1
            dwg.add(dwg.ellipse(center=(chain_x, chain_y), r=(2, 4),
                              fill='none', stroke=self.colors['symbols'],
                              stroke_width='1.5'))

    def _draw_round_2(self, dwg):
        """
        Round 2: Corner groups (3 dc, ch 2, 3 dc) at each corner
        """
        corner_distance = 80
        corner_angles = [45, 135, 225, 315]

        for angle in corner_angles:
            # Calculate corner position
            corner_x = self.center_x + corner_distance * math.cos(math.radians(angle))
            corner_y = self.center_y + corner_distance * math.sin(math.radians(angle))

            # Draw corner group: 3 dc, ch 2, 3 dc
            self._draw_corner_group_flowing(dwg, corner_x, corner_y, angle)

    def _draw_flowing_dc_cluster(self, dwg, x: float, y: float, angle: float, count: int):
        """Draw a cluster of dc stitches with flowing connections"""
        stitch_spacing = 8
        start_offset = -(count - 1) * stitch_spacing / 2

        # Calculate perpendicular direction for stitch arrangement
        perp_angle = angle + 90

        for i in range(count):
            offset = start_offset + i * stitch_spacing

            # Position each stitch
            stitch_x = x + offset * math.cos(math.radians(perp_angle))
            stitch_y = y + offset * math.sin(math.radians(perp_angle))

            # Draw dc symbol (T with two bars)
            self._draw_dc_symbol_flowing(dwg, stitch_x, stitch_y)

            # Draw connection line to center/previous round
            self._draw_stitch_connection(dwg, stitch_x, stitch_y, x, y)

    def _draw_dc_symbol_flowing(self, dwg, x: float, y: float):
        """Draw a clean dc symbol with minimal orientation complexity"""
        # Vertical line
        dwg.add(dwg.line(start=(x, y - 8), end=(x, y + 8),
                        stroke=self.colors['symbols'], stroke_width='1.5'))

        # Two horizontal bars
        dwg.add(dwg.line(start=(x - 3, y - 3), end=(x + 3, y - 3),
                        stroke=self.colors['symbols'], stroke_width='1'))
        dwg.add(dwg.line(start=(x - 3, y + 3), end=(x + 3, y + 3),
                        stroke=self.colors['symbols'], stroke_width='1'))

    def _draw_corner_group_flowing(self, dwg, x: float, y: float, angle: float):
        """Draw a flowing corner group: 3 dc, ch 2, 3 dc"""
        group_spacing = 15

        # Calculate positions for the two 3dc groups
        group1_x = x - group_spacing * math.cos(math.radians(angle))
        group1_y = y - group_spacing * math.sin(math.radians(angle))
        group2_x = x + group_spacing * math.cos(math.radians(angle))
        group2_y = y + group_spacing * math.sin(math.radians(angle))

        # Draw first 3 dc group
        self._draw_flowing_dc_cluster(dwg, group1_x, group1_y, angle, 3)

        # Draw second 3 dc group
        self._draw_flowing_dc_cluster(dwg, group2_x, group2_y, angle, 3)

        # Draw ch 2 space at corner (2 connected chain ovals)
        chain_offset = 8
        chain1_x = x + chain_offset * math.cos(math.radians(angle + 90))
        chain1_y = y + chain_offset * math.sin(math.radians(angle + 90))
        chain2_x = x - chain_offset * math.cos(math.radians(angle + 90))
        chain2_y = y - chain_offset * math.sin(math.radians(angle + 90))

        dwg.add(dwg.ellipse(center=(chain1_x, chain1_y), r=(2, 4),
                          fill='none', stroke=self.colors['symbols'],
                          stroke_width='1.5'))
        dwg.add(dwg.ellipse(center=(chain2_x, chain2_y), r=(2, 4),
                          fill='none', stroke=self.colors['symbols'],
                          stroke_width='1.5'))

        # Connect the chain ovals
        dwg.add(dwg.line(start=(chain1_x, chain1_y), end=(chain2_x, chain2_y),
                        stroke=self.colors['connections'], stroke_width='1'))

    def _draw_stitch_connection(self, dwg, from_x: float, from_y: float, to_x: float, to_y: float):
        """Draw connection line between stitches"""
        dwg.add(dwg.line(start=(from_x, from_y), end=(to_x, to_y),
                        stroke=self.colors['connections'],
                        stroke_width='0.8',
                        opacity='0.7'))

    def _draw_flowing_connections(self, dwg):
        """Draw the flowing connection lines that make the chart flow naturally"""
        # Round 1 corner positions
        r1_distance = 50
        r1_angles = [45, 135, 225, 315]

        # Round 2 corner positions
        r2_distance = 80
        r2_angles = [45, 135, 225, 315]

        # Connect each Round 1 corner to corresponding Round 2 corner
        for i, (r1_angle, r2_angle) in enumerate(zip(r1_angles, r2_angles)):
            r1_x = self.center_x + r1_distance * math.cos(math.radians(r1_angle))
            r1_y = self.center_y + r1_distance * math.sin(math.radians(r1_angle))

            r2_x = self.center_x + r2_distance * math.cos(math.radians(r2_angle))
            r2_y = self.center_y + r2_distance * math.sin(math.radians(r2_angle))

            # Draw flowing connection curve
            self._draw_curved_connection(dwg, r1_x, r1_y, r2_x, r2_y)

        # Connect center to Round 1 corners
        for angle in r1_angles:
            corner_x = self.center_x + r1_distance * math.cos(math.radians(angle))
            corner_y = self.center_y + r1_distance * math.sin(math.radians(angle))

            dwg.add(dwg.line(start=(self.center_x, self.center_y),
                           end=(corner_x, corner_y),
                           stroke=self.colors['connections'],
                           stroke_width='1',
                           opacity='0.6'))

    def _draw_curved_connection(self, dwg, x1: float, y1: float, x2: float, y2: float):
        """Draw a subtle curved connection between two points"""
        # Calculate midpoint for curve control
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2

        # Create a slight curve by offsetting the midpoint
        curve_offset = 5
        mid_x += curve_offset
        mid_y += curve_offset

        # Create curved path
        path_data = f"M {x1},{y1} Q {mid_x},{mid_y} {x2},{y2}"

        dwg.add(dwg.path(d=path_data,
                        stroke=self.colors['connections'],
                        stroke_width='1',
                        fill='none',
                        opacity='0.5'))

    def _draw_legend(self, dwg):
        """Draw a clean legend"""
        legend_x = 30
        legend_y = self.height - 80

        # Title
        dwg.add(dwg.text('Chart Symbols:',
                        insert=(legend_x, legend_y),
                        font_size='12px',
                        font_weight='bold',
                        fill=self.colors['text']))

        # Symbols
        symbols = [
            ('Double Crochet (dc)', 'dc'),
            ('Chain (ch)', 'chain'),
            ('Corner Space (ch-2)', 'corner')
        ]

        for i, (label, symbol_type) in enumerate(symbols):
            y = legend_y + 20 + (i * 16)

            if symbol_type == 'dc':
                self._draw_dc_symbol_flowing(dwg, legend_x + 10, y)
            elif symbol_type == 'chain':
                dwg.add(dwg.ellipse(center=(legend_x + 10, y), r=(2, 4),
                                  fill='none', stroke=self.colors['symbols'],
                                  stroke_width='1.5'))
            elif symbol_type == 'corner':
                dwg.add(dwg.ellipse(center=(legend_x + 8, y), r=(2, 3),
                                  fill='none', stroke=self.colors['symbols'],
                                  stroke_width='1.5'))
                dwg.add(dwg.ellipse(center=(legend_x + 12, y), r=(2, 3),
                                  fill='none', stroke=self.colors['symbols'],
                                  stroke_width='1.5'))

            # Label
            dwg.add(dwg.text(label,
                           insert=(legend_x + 25, y + 4),
                           font_size='10px',
                           fill=self.colors['text']))

# Global instance
flowing_granny_service = FlowingGrannyService()
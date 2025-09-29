"""
Professional Crochet Chart Generator using Matplotlib
Creates publication-quality crochet diagrams with proper polar layouts
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Circle, Wedge
import numpy as np
import io
import base64
from typing import Dict, List, Tuple
import math

class MatplotlibCrochetService:
    def __init__(self):
        # Set up matplotlib for clean, professional output
        plt.style.use('default')
        self.fig_size = (8, 8)  # Square figure for circular patterns
        self.dpi = 150  # High DPI for crisp output

        # Professional crochet chart colors
        self.colors = {
            'background': '#ffffff',
            'stitch_symbols': '#000000',
            'connection_lines': '#666666',
            'round_labels': '#000000',
            'guidelines': '#cccccc'
        }

        # Stitch symbol definitions
        self.stitch_symbols = {
            'chain': {'marker': 'o', 'size': 60, 'color': 'white', 'edgecolor': 'black', 'linewidth': 1.5},
            'single_crochet': {'marker': 'x', 'size': 80, 'color': 'black', 'linewidth': 2},
            'double_crochet': {'marker': '|', 'size': 100, 'color': 'black', 'linewidth': 2.5},
            'slip_stitch': {'marker': '.', 'size': 40, 'color': 'black'}
        }

    def generate_granny_square_chart(self, pattern_text: str = "") -> str:
        """
        Generate a professional granny square chart based on the actual pattern provided
        """
        print(f"DEBUG: matplotlib_crochet_service.generate_granny_square_chart called with pattern: {pattern_text[:100]}...")

        # Create figure with regular (not polar) subplot for better control
        fig, ax = plt.subplots(figsize=self.fig_size, dpi=self.dpi)

        # Configure the plot for professional appearance
        ax.set_facecolor(self.colors['background'])
        ax.set_aspect('equal')
        ax.axis('off')  # Remove axes for clean look

        # Analyze the pattern to determine structure
        if self._is_traditional_granny_pattern(pattern_text):
            print("DEBUG: Drawing traditional granny square")
            # Traditional granny square with ch-4 ring and corner ch-2 spaces
            self._draw_traditional_granny_square(ax, pattern_text)
        else:
            print("DEBUG: Drawing circular pattern fallback")
            # Default to the circular pattern we had before
            self._draw_round_1_cartesian(ax)
            self._draw_round_2_cartesian(ax)

        # Add title
        ax.set_title('Granny Square Pattern Chart',
                    fontsize=16, fontweight='bold', pad=20)

        # Set appropriate limits to show the pattern clearly with proper margins
        ax.set_xlim(-3.0, 3.0)
        ax.set_ylim(-3.0, 3.0)

        # Convert to SVG string
        svg_buffer = io.StringIO()
        plt.savefig(svg_buffer, format='svg', bbox_inches='tight',
                   facecolor=self.colors['background'], edgecolor='none')
        plt.close(fig)  # Clean up memory

        svg_string = svg_buffer.getvalue()
        svg_buffer.close()

        return svg_string

    def _is_traditional_granny_pattern(self, pattern_text: str) -> bool:
        """Check if this is a traditional granny square pattern"""
        if not pattern_text:
            return False

        pattern_lower = pattern_text.lower()

        # First check for general granny square requests
        general_granny_indicators = [
            'granny square' in pattern_lower,
            'granny' in pattern_lower and 'square' in pattern_lower,
        ]

        # Also check for specific technical pattern indicators
        technical_indicators = [
            'ch 4' in pattern_lower and 'join' in pattern_lower,
            'ch 2' in pattern_lower,
            'ch-2 sp' in pattern_lower,
            'corner' in pattern_lower,
            '3 dc' in pattern_lower and 'ch 1' in pattern_lower and 'ch 2' in pattern_lower
        ]

        # Return True if either general or technical indicators are found
        return any(general_granny_indicators) or any(technical_indicators)

    def _draw_traditional_granny_square(self, ax, pattern_text: str):
        """Draw a traditional granny square with proper round progression"""
        # Draw foundation ring (ch-4)
        foundation_circle = plt.Circle((0, 0), 0.2, fill=False, edgecolor='black', linewidth=2)
        ax.add_patch(foundation_circle)
        ax.text(0, 0, 'Ch 4\nRing', ha='center', va='center', fontsize=8, fontweight='bold')

        # Draw guideline squares to help with positioning
        self._draw_square_framework(ax, 1.4, color='lightblue', alpha=0.3)  # Round 2 square
        self._draw_square_framework(ax, 2.2, color='lightgreen', alpha=0.3)  # Round 3 square

        # Round 2: First actual granny round - 4 corner groups (3 dc, ch 2) in the ring
        self._draw_granny_round_2(ax)

        # Round 3: Work into ch-2 spaces - corner groups with ch 1 between sides
        self._draw_granny_round_3(ax)

        # Add slip stitch marker (within bounds)
        self._draw_slst(ax, 0, 2.8)

    def _draw_granny_round_2(self, ax):
        """Round 2: [3 dc, ch 2, 3 dc] corner groups at each corner"""
        # Round 2 positions (outer square)
        r2_size = 1.4

        # Define corners: North, East, South, West
        corners = [
            (0, r2_size),      # North
            (r2_size, 0),      # East
            (0, -r2_size),     # South
            (-r2_size, 0)      # West
        ]

        # Draw corner groups: [3 dc, ch 2, 3 dc] at each corner
        for i, (cx, cy) in enumerate(corners):
            # Draw the corner group structure
            self._draw_round2_corner_group(ax, cx, cy)

    def _draw_round2_corner_group(self, ax, cx: float, cy: float):
        """Draw Round 2 corner group: Simple 3 dc cluster at each corner"""
        # Position 3 DC stitches in a VERY tight cluster at corner
        dc_positions = []
        tight_spacing = 0.12  # Much tighter spacing for proper clustering
        if cx == 0:  # North or South corner
            dc_positions = [
                (cx - tight_spacing, cy),  # Left DC
                (cx, cy),                   # Center DC
                (cx + tight_spacing, cy)    # Right DC
            ]
        else:  # East or West corner
            dc_positions = [
                (cx, cy - tight_spacing),  # Bottom DC
                (cx, cy),                  # Center DC
                (cx, cy + tight_spacing)   # Top DC
            ]

        # Draw the 3 DC cluster
        for dx, dy in dc_positions:
            self._draw_simple_dc(ax, dx, dy)

        # Draw ch 2 corner space directly AT the corner position
        # Don't offset it - place it exactly at the corner where it belongs
        self._draw_angled_ch2_corner(ax, cx, cy, cx, cy)

    def _draw_angled_ch2_corner(self, ax, ch2_x: float, ch2_y: float, corner_x: float, corner_y: float):
        """Draw ch-2 corner as two angled chain ovals forming a right angle at each square corner"""
        chain_width = 0.10
        chain_height = 0.16
        corner_offset = 0.15

        # Determine which corner this is based on actual Round 2 coordinates
        # Round 2 uses: North (0, 1.4), East (1.4, 0), South (0, -1.4), West (-1.4, 0)

        if abs(corner_x) < 0.1 and corner_y > 0:  # North corner (0, 1.4)
            # Position ch-2 in NE direction to form right angle
            chain1_x = corner_x + corner_offset
            chain1_y = corner_y + corner_offset
            chain2_x = corner_x + corner_offset
            chain2_y = corner_y
        elif corner_x > 0 and abs(corner_y) < 0.1:  # East corner (1.4, 0)
            # Position ch-2 in SE direction to form right angle
            chain1_x = corner_x + corner_offset
            chain1_y = corner_y - corner_offset
            chain2_x = corner_x
            chain2_y = corner_y - corner_offset
        elif abs(corner_x) < 0.1 and corner_y < 0:  # South corner (0, -1.4)
            # Position ch-2 in SW direction to form right angle
            chain1_x = corner_x - corner_offset
            chain1_y = corner_y - corner_offset
            chain2_x = corner_x - corner_offset
            chain2_y = corner_y
        else:  # West corner (-1.4, 0)
            # Position ch-2 in NW direction to form right angle
            chain1_x = corner_x - corner_offset
            chain1_y = corner_y + corner_offset
            chain2_x = corner_x
            chain2_y = corner_y + corner_offset

        # Draw the two chain ovals forming a right angle
        ellipse1 = patches.Ellipse((chain1_x, chain1_y), chain_width, chain_height,
                                  fill=False, edgecolor='black', linewidth=2.5)
        ellipse2 = patches.Ellipse((chain2_x, chain2_y), chain_width, chain_height,
                                  fill=False, edgecolor='black', linewidth=2.5)
        ax.add_patch(ellipse1)
        ax.add_patch(ellipse2)

    def _draw_corner_ch2_space(self, ax, angle: float, radius: float):
        """Draw ch-2 corner space with proper right-angle formation like reference image"""
        # Create two chain ovals that form a proper right angle (90 degrees)
        # Position them perpendicular to create corner effect

        # Calculate perpendicular angles for right-angle formation
        perp_offset = np.pi/4  # 45 degrees offset for right angle

        # First chain oval - positioned at angle - 45°
        chain1_angle = angle - perp_offset
        self._draw_chain(ax, chain1_angle, radius, width=0.08, height=0.15)

        # Second chain oval - positioned at angle + 45°
        chain2_angle = angle + perp_offset
        self._draw_chain(ax, chain2_angle, radius, width=0.08, height=0.15)

    def _draw_square_framework(self, ax, size: float, color: str = 'lightgray', alpha: float = 0.5):
        """Draw a square framework to guide stitch placement"""
        # Draw square outline with better visibility
        square_x = [-size, size, size, -size, -size]
        square_y = [size, size, -size, -size, size]
        ax.plot(square_x, square_y, color=color, linewidth=1.5, alpha=alpha, linestyle='-')

        # Add corner markers to show where stitches connect
        corner_size = 0.05
        corners = [(-size, size), (size, size), (size, -size), (-size, -size)]
        for corner_x, corner_y in corners:
            circle = patches.Circle((corner_x, corner_y), corner_size,
                                   fill=True, facecolor=color, alpha=alpha*2)
            ax.add_patch(circle)

    def _draw_simple_dc(self, ax, x: float, y: float):
        """Draw a proper double crochet symbol oriented toward center"""
        # Calculate angle from this position to center (0,0)
        angle_to_center = np.arctan2(-y, -x)  # Point toward center

        # DC symbol dimensions - improved proportions for better T appearance
        height = 0.35
        bar_width = 0.18  # Wider bars for better visibility
        stem_width = 2.5  # Thicker stem for professional look

        # Calculate the stem line (pointing toward center)
        stem_start_x = x
        stem_start_y = y
        stem_end_x = x + height * np.cos(angle_to_center)
        stem_end_y = y + height * np.sin(angle_to_center)

        # Draw main stem pointing toward center (thicker for better appearance)
        ax.plot([stem_start_x, stem_end_x], [stem_start_y, stem_end_y],
                color='black', linewidth=stem_width)

        # Calculate perpendicular direction for crossbars
        perp_angle = angle_to_center + np.pi/2

        # Draw traditional double crochet: one crossbar at end, one in middle

        # Crossbar at the starting end (outer end)
        bar_start_x = stem_start_x - (bar_width/2) * np.cos(perp_angle)
        bar_start_y = stem_start_y - (bar_width/2) * np.sin(perp_angle)
        bar_end_x = stem_start_x + (bar_width/2) * np.cos(perp_angle)
        bar_end_y = stem_start_y + (bar_width/2) * np.sin(perp_angle)

        ax.plot([bar_start_x, bar_end_x], [bar_start_y, bar_end_y],
                color='black', linewidth=2.0)

        # Crossbar in the MIDDLE of the stem (traditional DC appearance)
        mid_x = stem_start_x + (height/2) * np.cos(angle_to_center)
        mid_y = stem_start_y + (height/2) * np.sin(angle_to_center)

        bar_start_x = mid_x - (bar_width/2) * np.cos(perp_angle)
        bar_start_y = mid_y - (bar_width/2) * np.sin(perp_angle)
        bar_end_x = mid_x + (bar_width/2) * np.cos(perp_angle)
        bar_end_y = mid_y + (bar_width/2) * np.sin(perp_angle)

        ax.plot([bar_start_x, bar_end_x], [bar_start_y, bar_end_y],
                color='black', linewidth=2.0)

    def _draw_simple_ch2_corner(self, ax, corner1: tuple, corner2: tuple):
        """Draw simple ch-2 corner space between two corners with better appearance"""
        # Calculate corner position (should be at actual corner, not midpoint)
        # Find the corner point
        corner_x = corner1[0] if abs(corner1[0]) > abs(corner1[1]) else corner2[0]
        corner_y = corner1[1] if abs(corner1[1]) > abs(corner1[0]) else corner2[1]

        # Draw two chain ovals at the corner forming an angle - improved appearance
        chain_width = 0.10   # Slightly wider for better visibility
        chain_height = 0.16  # Taller for better proportions
        offset = 0.18        # Increased offset for better corner definition

        # Position chains to form a proper corner angle
        if corner_x == 0:  # Top or bottom corner
            chain1_x = corner_x - offset
            chain1_y = corner_y
            chain2_x = corner_x + offset
            chain2_y = corner_y
        else:  # Left or right corner
            chain1_x = corner_x
            chain1_y = corner_y - offset
            chain2_x = corner_x
            chain2_y = corner_y + offset

        # Draw chain ovals with thicker lines to match DC symbols
        ellipse1 = patches.Ellipse((chain1_x, chain1_y), chain_width, chain_height,
                                  fill=False, edgecolor='black', linewidth=2.0)
        ellipse2 = patches.Ellipse((chain2_x, chain2_y), chain_width, chain_height,
                                  fill=False, edgecolor='black', linewidth=2.0)
        ax.add_patch(ellipse1)
        ax.add_patch(ellipse2)

    def _draw_chain_line_to_corner(self, ax, start_x: float, start_y: float, end_x: float, end_y: float, num_chains: int = 3):
        """Draw a line of chains from center toward corner (fallback method)"""
        # Use the new prominent ch 3 method
        self._draw_ch3_as_first_dc(ax, start_x, start_y, end_x, end_y)

    def _draw_dc_group_at_corner(self, ax, x: float, y: float, count: int = 3):
        """Draw a group of dc stitches with top crossbar positioned ON the square edge"""
        # Position DC stitches along the square edge with top crossbar ON the edge
        spacing = 0.12  # Tighter spacing between DC stitches
        start_offset = -(count - 1) * spacing / 2

        for i in range(count):
            # Calculate position along the square edge
            offset = start_offset + i * spacing

            # Position each DC so the TOP CROSSBAR sits exactly on the square edge
            dc_height = 0.3  # Height of the DC symbol

            if abs(x) > abs(y):  # On left or right edge
                # Position DC so top crossbar is on the edge
                dc_x = x - (dc_height / 2) if x > 0 else x + (dc_height / 2)
                dc_y = y + offset
                dc_angle = 0 if x > 0 else np.pi  # Point toward center
            else:  # On top or bottom edge
                dc_x = x + offset
                # Position DC so top crossbar is on the edge
                dc_y = y - (dc_height / 2) if y > 0 else y + (dc_height / 2)
                dc_angle = np.pi/2 if y > 0 else -np.pi/2  # Point toward center

            # Draw DC symbol with precise positioning
            self._draw_dc(ax, dc_angle, np.sqrt(dc_x**2 + dc_y**2), height=dc_height)

    def _draw_ch2_corner_space(self, ax, x1: float, y1: float, x2: float, y2: float):
        """Draw ch-2 corner space exactly at the square corner"""
        # Position ch-2 exactly at the corner between the two adjacent corners
        # Find the actual square corner position
        corner_x = x1 if abs(x1) > abs(y1) else x2
        corner_y = y1 if abs(y1) > abs(x1) else y2

        # Ensure we get the proper corner position
        if abs(x1) > abs(y1) and abs(x2) > abs(y2):  # Both on vertical edges
            corner_x = (x1 + x2) / 2
            corner_y = max(y1, y2) if y1 * y2 > 0 else min(abs(y1), abs(y2)) * (1 if y1 > y2 else -1)
        elif abs(y1) > abs(x1) and abs(y2) > abs(x2):  # Both on horizontal edges
            corner_x = max(x1, x2) if x1 * x2 > 0 else min(abs(x1), abs(x2)) * (1 if x1 > x2 else -1)
            corner_y = (y1 + y2) / 2

        # Position two chain ovals to form an angle exactly at the corner
        offset = 0.12
        angle1 = np.arctan2(y1, x1)
        angle2 = np.arctan2(y2, x2)

        # Position chains to form a corner angle
        chain1_x = corner_x - offset * np.cos(angle1 + np.pi/4)
        chain1_y = corner_y - offset * np.sin(angle1 + np.pi/4)
        chain2_x = corner_x - offset * np.cos(angle2 - np.pi/4)
        chain2_y = corner_y - offset * np.sin(angle2 - np.pi/4)

        # Draw the two chain ovals forming the corner
        ellipse1 = patches.Ellipse((chain1_x, chain1_y), 0.08, 0.12,
                                  angle=np.degrees(angle1), fill=False, edgecolor='black', linewidth=1.5)
        ellipse2 = patches.Ellipse((chain2_x, chain2_y), 0.08, 0.12,
                                  angle=np.degrees(angle2), fill=False, edgecolor='black', linewidth=1.5)
        ax.add_patch(ellipse1)
        ax.add_patch(ellipse2)

    def _draw_granny_round_3(self, ax):
        """Round 3: Simple clean approach matching reference image"""
        # Round 3 positions (larger outer square)
        r3_size = 2.2

        # Corner positions
        corners = [
            (0, r3_size),      # North
            (r3_size, 0),      # East
            (0, -r3_size),     # South
            (-r3_size, 0)      # West
        ]

        # Draw corner groups [3 dc, ch 2, 3 dc] at each corner ONLY
        for i, (cx, cy) in enumerate(corners):
            # Position 3 DC stitches in a tight cluster at corner (like Round 2)
            dc_positions = []
            if cx == 0:  # North or South corner
                dc_positions = [
                    (cx - 0.2, cy),  # Left DC
                    (cx, cy),        # Center DC
                    (cx + 0.2, cy)   # Right DC
                ]
            else:  # East or West corner
                dc_positions = [
                    (cx, cy - 0.2),  # Bottom DC
                    (cx, cy),        # Center DC
                    (cx, cy + 0.2)   # Top DC
                ]

            # Draw the 3 DC cluster
            for dx, dy in dc_positions:
                self._draw_simple_dc(ax, dx, dy)

            # Draw ch 2 corner space
            self._draw_simple_corner_ch2(ax, cx, cy)

        # Add ONLY ch 1 connecting chains between corners (no extra DC groups)
        side_positions = [
            (r3_size * 0.7, r3_size * 0.7),    # NE - between North and East corners
            (r3_size * 0.7, -r3_size * 0.7),   # SE - between East and South corners
            (-r3_size * 0.7, -r3_size * 0.7),  # SW - between South and West corners
            (-r3_size * 0.7, r3_size * 0.7)    # NW - between West and North corners
        ]

        for sx, sy in side_positions:
            self._draw_simple_ch1(ax, sx, sy)

    def _draw_simple_corner_ch2(self, ax, x: float, y: float):
        """Draw ch-2 space at corner with improved appearance"""
        chain_width = 0.10   # Wider for better visibility
        chain_height = 0.15  # Better proportions
        # Position two chains at the corner
        ellipse1 = patches.Ellipse((x - 0.12, y + 0.12), chain_width, chain_height,
                                  fill=False, edgecolor='black', linewidth=2.0)
        ellipse2 = patches.Ellipse((x + 0.12, y - 0.12), chain_width, chain_height,
                                  fill=False, edgecolor='black', linewidth=2.0)
        ax.add_patch(ellipse1)
        ax.add_patch(ellipse2)

    def _draw_simple_ch1(self, ax, x: float, y: float):
        """Draw single ch-1 space with improved appearance"""
        chain_width = 0.08   # Consistent with improved sizing
        chain_height = 0.12  # Better proportions
        ellipse = patches.Ellipse((x, y), chain_width, chain_height,
                                 fill=False, edgecolor='black', linewidth=2.0)
        ax.add_patch(ellipse)

    def _draw_corner_group_round3(self, ax, x: float, y: float, start_with_ch3: bool = False):
        """Draw a complete corner group for Round 3: [3 dc, ch 2, 3 dc]"""
        angle = np.arctan2(y, x)

        if start_with_ch3:
            # Already drew ch 3, now draw 2 more dc + ch 2 + 3 dc
            self._draw_dc_group_at_corner(ax, x - 0.1, y - 0.1, count=2)  # Complete first group
            self._draw_dc_group_at_corner(ax, x + 0.1, y + 0.1, count=3)  # Second group
        else:
            # Draw full [3 dc, ch 2, 3 dc] corner group
            self._draw_dc_group_at_corner(ax, x - 0.1, y - 0.1, count=3)  # First group
            self._draw_dc_group_at_corner(ax, x + 0.1, y + 0.1, count=3)  # Second group

        # Draw ch 2 corner space
        offset = 0.15
        chain1_x = x + offset * np.cos(angle - 0.3)
        chain1_y = y + offset * np.sin(angle - 0.3)
        chain2_x = x + offset * np.cos(angle + 0.3)
        chain2_y = y + offset * np.sin(angle + 0.3)

        ellipse1 = patches.Ellipse((chain1_x, chain1_y), 0.08, 0.15,
                                  angle=np.degrees(angle - 0.3),
                                  fill=False, edgecolor='black', linewidth=1.5)
        ellipse2 = patches.Ellipse((chain2_x, chain2_y), 0.08, 0.15,
                                  angle=np.degrees(angle + 0.3),
                                  fill=False, edgecolor='black', linewidth=1.5)
        ax.add_patch(ellipse1)
        ax.add_patch(ellipse2)

    def _draw_dc(self, ax, angle, radius, height=0.6, width=0.15, color="black"):
        """Draw a double crochet stitch using traditional 'double T' symbol"""
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)

        # Calculate the orientation - stem points toward center
        toward_center_angle = angle + np.pi  # Point toward center
        perp_angle = angle + np.pi/2  # Perpendicular for crossbars

        # Main vertical line (stem of the T pointing toward center)
        stem_start_x = x  # Start at the stitch position
        stem_start_y = y
        stem_end_x = x + height * np.cos(toward_center_angle)
        stem_end_y = y + height * np.sin(toward_center_angle)

        ax.plot([stem_start_x, stem_end_x], [stem_start_y, stem_end_y],
                color=color, linewidth=2)

        # Two horizontal crossbars for double crochet
        bar_length = width

        # First crossbar at the top (at the stitch position)
        bar1_x = stem_start_x
        bar1_y = stem_start_y
        bar1_start_x = bar1_x - (bar_length/2) * np.cos(perp_angle)
        bar1_start_y = bar1_y - (bar_length/2) * np.sin(perp_angle)
        bar1_end_x = bar1_x + (bar_length/2) * np.cos(perp_angle)
        bar1_end_y = bar1_y + (bar_length/2) * np.sin(perp_angle)

        ax.plot([bar1_start_x, bar1_end_x], [bar1_start_y, bar1_end_y],
                color=color, linewidth=1.5)

        # Second crossbar halfway down the stem
        bar2_x = x + (height/2) * np.cos(toward_center_angle)
        bar2_y = y + (height/2) * np.sin(toward_center_angle)
        bar2_start_x = bar2_x - (bar_length/2) * np.cos(perp_angle)
        bar2_start_y = bar2_y - (bar_length/2) * np.sin(perp_angle)
        bar2_end_x = bar2_x + (bar_length/2) * np.cos(perp_angle)
        bar2_end_y = bar2_y + (bar_length/2) * np.sin(perp_angle)

        ax.plot([bar2_start_x, bar2_end_x], [bar2_start_y, bar2_end_y],
                color=color, linewidth=1.5)

    def _draw_sc(self, ax, angle, radius, size=0.3, color="black"):
        """Draw a single crochet stitch using traditional X symbol"""
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)

        # Draw X pattern for single crochet
        half_size = size / 2
        # First diagonal line
        ax.plot([x - half_size, x + half_size], [y - half_size, y + half_size],
                color=color, linewidth=1.5)
        # Second diagonal line
        ax.plot([x - half_size, x + half_size], [y + half_size, y - half_size],
                color=color, linewidth=1.5)

    def _draw_chain(self, ax, angle, radius, width=0.08, height=0.15, color="black"):
        """Draw chain stitch using traditional oblong/oval symbol"""
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)

        # Create oblong/oval shape for chain (oriented along the radius)
        ellipse = patches.Ellipse((x, y), width, height, angle=np.degrees(angle),
                                 fill=False, edgecolor=color, linewidth=1.5)
        ax.add_patch(ellipse)

    def _draw_slst(self, ax, angle, radius, size=0.1, color="red"):
        """Draw slip stitch (filled dot) - ChatGPT's approach"""
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        circle = plt.Circle((x, y), size, color=color)
        ax.add_patch(circle)

    def _draw_round_1_cartesian(self, ax):
        """Round 1: 12 dc in magic ring (following ChatGPT's pattern)"""
        num_stitches_r1 = 12  # ch 3 + 11 dc = 12 total stitches
        radius_r1 = 1.5

        for i in range(num_stitches_r1):
            angle = 2 * np.pi * i / num_stitches_r1
            self._draw_dc(ax, angle, radius_r1)

        # Draw magic ring in center
        center_circle = plt.Circle((0, 0), 0.3, fill=False, edgecolor='black', linewidth=2)
        ax.add_patch(center_circle)
        ax.text(0, 0, 'Magic\nRing', ha='center', va='center', fontsize=8, fontweight='bold')

    def _draw_round_2_cartesian(self, ax):
        """Round 2: 12 groups of 3 dc (one group worked into each dc from Round 1) with chain spaces"""
        # Round 2 should have 12 clusters of 3 dc each (matching the 12 dc from Round 1)
        # Plus chain spaces between them
        num_clusters = 12  # One cluster for each dc from Round 1
        radius_r2 = 3.0

        for i in range(num_clusters):
            # Calculate base angle for each cluster (evenly distributed around circle)
            base_angle = 2 * np.pi * i / num_clusters

            # Draw 3 dc cluster
            for j in range(3):
                offset = (j - 1) * 0.08  # Spread the 3 dc slightly (smaller offset for tighter clusters)
                self._draw_dc(ax, base_angle + offset, radius_r2)

            # Draw chain space between each cluster
            # In granny square Round 2: [ch 1, 3 dc in next st] around means ch 1 between every 3 dc group
            chain_angle = base_angle + (np.pi / num_clusters)  # Between current and next cluster
            self._draw_chain(ax, chain_angle, radius_r2 + 0.3)

        # Add slip stitch marker
        self._draw_slst(ax, 0, radius_r2 + 0.6)

    def _draw_foundation_ring_matplotlib(self, ax):
        """Draw the foundation chain ring in center using matplotlib"""
        # Draw small circle representing the magic ring/foundation
        center_circle = Circle((0, 0), 0.15, transform=ax.transData._b,
                             facecolor='none', edgecolor=self.colors['stitch_symbols'],
                             linewidth=2, zorder=10)
        ax.add_patch(center_circle)

        # Add center label
        ax.text(0, 0, 'Magic\nRing', ha='center', va='center',
               fontsize=8, fontweight='bold', transform=ax.transData._b)

    def _draw_round_1_matplotlib(self, ax):
        """
        Round 1: 4 corners with 3 dc each at the corners of a square
        """
        # Square corners at 45, 135, 225, 315 degrees
        corner_angles = [45, 135, 225, 315]
        radius = 0.6  # Distance from center

        for i, angle_deg in enumerate(corner_angles):
            angle_rad = np.radians(angle_deg)

            # Draw 3 dc cluster at each corner
            self._draw_dc_cluster_matplotlib(ax, angle_rad, radius, 3)

            # Add corner chain space between clusters
            if i < len(corner_angles) - 1:
                next_angle = corner_angles[i + 1]
            else:
                next_angle = corner_angles[0]

            mid_angle = np.radians((angle_deg + next_angle) / 2)
            if mid_angle < angle_rad:  # Handle wrap-around
                mid_angle += np.pi

            # Draw chain space
            chain_radius = radius * 0.8
            ax.scatter(mid_angle, chain_radius,
                      **self.stitch_symbols['chain'], zorder=5)

    def _draw_round_2_matplotlib(self, ax):
        """
        Round 2: Corner groups (3 dc, ch 2, 3 dc) at each corner
        """
        corner_angles = [45, 135, 225, 315]
        radius = 1.0  # Larger radius for round 2

        for angle_deg in corner_angles:
            angle_rad = np.radians(angle_deg)

            # Draw corner group: 3 dc, ch 2, 3 dc
            self._draw_corner_group_matplotlib(ax, angle_rad, radius)

    def _draw_dc_cluster_matplotlib(self, ax, angle: float, radius: float, count: int):
        """Draw a cluster of double crochet stitches"""
        # Calculate positions for the cluster
        angular_spread = 0.2  # Spread the stitches across this angle
        start_angle = angle - angular_spread / 2

        for i in range(count):
            if count > 1:
                stitch_angle = start_angle + (i * angular_spread / (count - 1))
            else:
                stitch_angle = angle

            # Draw double crochet symbol
            ax.scatter(stitch_angle, radius,
                      **self.stitch_symbols['double_crochet'], zorder=5)

            # Draw connection line to center
            ax.plot([stitch_angle, stitch_angle], [0.2, radius],
                   color=self.colors['connection_lines'],
                   linewidth=1, alpha=0.6, zorder=1)

    def _draw_corner_group_matplotlib(self, ax, angle: float, radius: float):
        """Draw a corner group: 3 dc, ch 2, 3 dc"""
        group_spread = 0.3  # Angular spread for the entire corner group

        # First 3 dc group
        group1_angle = angle - group_spread / 3
        self._draw_dc_cluster_matplotlib(ax, group1_angle, radius, 3)

        # Chain 2 space in the middle
        chain_angles = [angle - 0.05, angle + 0.05]  # Two chain symbols
        for chain_angle in chain_angles:
            ax.scatter(chain_angle, radius + 0.1,
                      **self.stitch_symbols['chain'], zorder=5)

        # Second 3 dc group
        group2_angle = angle + group_spread / 3
        self._draw_dc_cluster_matplotlib(ax, group2_angle, radius, 3)

    def _add_matplotlib_legend(self, fig):
        """Add a professional legend to the chart"""
        # Create legend elements
        legend_elements = []

        # Add stitch symbol explanations
        symbols = [
            ('Double Crochet (dc)', 'double_crochet'),
            ('Chain (ch)', 'chain'),
            ('Magic Ring', 'slip_stitch')
        ]

        for label, symbol_key in symbols:
            if symbol_key in self.stitch_symbols:
                symbol = self.stitch_symbols[symbol_key]
                element = plt.Line2D([0], [0], marker=symbol['marker'],
                                   color='w', markerfacecolor=symbol.get('color', 'black'),
                                   markersize=8, label=label, linewidth=0,
                                   markeredgecolor=symbol.get('edgecolor', 'black'))
                legend_elements.append(element)

        # Add legend to figure
        fig.legend(handles=legend_elements, loc='lower center',
                  bbox_to_anchor=(0.5, 0.02), ncol=3, frameon=False)

    def generate_pattern_chart(self, pattern_data: Dict) -> str:
        """
        Generate a chart for any parsed pattern data
        """
        if pattern_data.get('pattern_type') == 'granny_square':
            return self.generate_granny_square_chart()
        else:
            # For other patterns, use a more general approach
            return self.generate_general_pattern_chart(pattern_data)

    def generate_general_pattern_chart(self, pattern_data: Dict) -> str:
        """
        Generate a chart for general crochet patterns
        """
        fig, ax = plt.subplots(figsize=self.fig_size, dpi=self.dpi, subplot_kw=dict(projection='polar'))

        # Configure polar plot
        ax.set_facecolor(self.colors['background'])
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        ax.set_rticks([])
        ax.set_thetagrids([])
        ax.grid(False)

        # Draw rounds based on pattern data
        rounds = pattern_data.get('rounds', [])
        for i, round_data in enumerate(rounds[:4]):  # Limit to 4 rounds for clarity
            radius = 0.3 + (i * 0.3)  # Increasing radius for each round
            self._draw_general_round(ax, round_data, radius)

        # Add title
        pattern_type = pattern_data.get('pattern_type', 'Crochet Pattern').title()
        ax.set_title(f'{pattern_type} Chart', fontsize=16, fontweight='bold', pad=20)

        # Convert to SVG
        svg_buffer = io.StringIO()
        plt.savefig(svg_buffer, format='svg', bbox_inches='tight',
                   facecolor=self.colors['background'], edgecolor='none')
        plt.close(fig)

        svg_string = svg_buffer.getvalue()
        svg_buffer.close()

        return svg_string

    def _draw_general_round(self, ax, round_data: Dict, radius: float):
        """Draw a general round based on stitch data"""
        stitches = round_data.get('stitches', [])
        if not stitches:
            return

        # Distribute stitches evenly around the circle
        angles = np.linspace(0, 2*np.pi, len(stitches), endpoint=False)

        for angle, stitch in zip(angles, stitches):
            stitch_type = stitch.get('type', 'single_crochet')

            # Map stitch types to symbols
            if 'dc' in stitch_type or 'double' in stitch_type:
                symbol_key = 'double_crochet'
            elif 'ch' in stitch_type or 'chain' in stitch_type:
                symbol_key = 'chain'
            else:
                symbol_key = 'single_crochet'

            # Draw the stitch
            if symbol_key in self.stitch_symbols:
                ax.scatter(angle, radius, **self.stitch_symbols[symbol_key], zorder=5)

# Global instance
matplotlib_crochet_service = MatplotlibCrochetService()
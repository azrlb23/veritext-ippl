import html
import os
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = "/System/Library/Fonts/Supplemental/Arial.ttf"
if not os.path.exists(FONT_PATH):
    FONT_PATH = "/System/Library/Fonts/Helvetica.ttc"

class DrawioWriter:
    def __init__(self, diagram_id, diagram_name, width=1400, height=1200):
        self.diagram_id = diagram_id
        self.diagram_name = diagram_name
        self.width = width
        self.height = height
        self.nodes = []
        self.edges = []
        self._cell_id = 100

    def next_id(self):
        self._cell_id += 1
        return f"cell_{self._cell_id}"

    def add_node(self, cell_id, value, x, y, w, h, style):
        escaped_val = html.escape(value).replace("\n", "&#xa;")
        node_xml = f'        <mxCell id="{cell_id}" value="{escaped_val}" style="{style}" vertex="1" parent="1">\n'
        node_xml += f'          <mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry" />\n'
        node_xml += f'        </mxCell>'
        self.nodes.append(node_xml)

    def add_edge(self, edge_id, source=None, target=None, value="", style="", waypoints=None, source_point=None, target_point=None):
        escaped_val = html.escape(value).replace("\n", "&#xa;") if value else ""
        lbl_attr = f'value="{escaped_val}" ' if escaped_val else ''
        src_attr = f'source="{source}" ' if source else ''
        tgt_attr = f'target="{target}" ' if target else ''
        edge_xml = f'        <mxCell id="{edge_id}" {lbl_attr}{src_attr}{tgt_attr}style="{style}" edge="1" parent="1">\n'
        edge_xml += f'          <mxGeometry relative="1" as="geometry">\n'
        if source_point:
            edge_xml += f'            <mxPoint x="{source_point[0]}" y="{source_point[1]}" as="sourcePoint" />\n'
        if target_point:
            edge_xml += f'            <mxPoint x="{target_point[0]}" y="{target_point[1]}" as="targetPoint" />\n'
        if waypoints:
            edge_xml += f'            <Array as="points">\n'
            for px, py in waypoints:
                edge_xml += f'              <mxPoint x="{px}" y="{py}" />\n'
            edge_xml += f'            </Array>\n'
        edge_xml += f'          </mxGeometry>\n'
        edge_xml += f'        </mxCell>'
        self.edges.append(edge_xml)

    def to_xml(self):
        xml = ['<mxfile host="app.diagrams.net" modified="2026-11-07T12:00:00.000Z" agent="Mozilla/5.0" version="24.0.0" type="device">']
        xml.append(f'  <diagram id="{self.diagram_id}" name="{html.escape(self.diagram_name)}">')
        xml.append(f'    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="{self.width}" pageHeight="{self.height}" background="#FFFFFF" math="0" shadow="0">')
        xml.append('      <root>')
        xml.append('        <mxCell id="0" />')
        xml.append('        <mxCell id="1" parent="0" />')
        for node in self.nodes:
            xml.append(node)
        for edge in self.edges:
            xml.append(edge)
        xml.append('      </root>')
        xml.append('    </mxGraphModel>')
        xml.append('  </diagram>')
        xml.append('</mxfile>')
        return '\n'.join(xml)

    def save(self, filepath):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.to_xml())


class PngCanvas:
    def __init__(self, width=1200, height=900, scale=2):
        self.width = width
        self.height = height
        self.scale = scale
        self.w = int(width * scale)
        self.h = int(height * scale)
        self.img = Image.new("RGB", (self.w, self.h), "#FFFFFF")
        self.draw = ImageDraw.Draw(self.img)

    def _f(self, val):
        return int(val * self.scale)

    def get_font(self, size, bold=False):
        scaled_size = int(size * self.scale)
        try:
            return ImageFont.truetype(FONT_PATH, scaled_size)
        except Exception:
            return ImageFont.load_default()

    def draw_header(self, title="", subtitle=None):
        # Strict user instruction: Do NOT add title or header at the top left of diagrams!
        pass

    def draw_stickman(self, x, y, w, h, label=""):
        """Draws standard UML stickman actor in plain black and white."""
        cx = self._f(x + w / 2)
        top_y = self._f(y)
        head_r = self._f(15)
        
        # Head (circle)
        self.draw.ellipse([cx - head_r, top_y, cx + head_r, top_y + 2 * head_r], fill="#FFFFFF", outline="#000000", width=self._f(2))
        
        # Body (vertical line)
        neck_y = top_y + 2 * head_r
        body_len = self._f(32)
        pelvis_y = neck_y + body_len
        self.draw.line([(cx, neck_y), (cx, pelvis_y)], fill="#000000", width=self._f(2))
        
        # Arms (horizontal line)
        arm_y = neck_y + self._f(10)
        arm_span = self._f(22)
        self.draw.line([(cx - arm_span, arm_y), (cx + arm_span, arm_y)], fill="#000000", width=self._f(2))
        
        # Legs (two diagonal lines)
        leg_len = self._f(30)
        leg_span = self._f(18)
        foot_y = pelvis_y + leg_len
        self.draw.line([(cx, pelvis_y), (cx - leg_span, foot_y)], fill="#000000", width=self._f(2))
        self.draw.line([(cx, pelvis_y), (cx + leg_span, foot_y)], fill="#000000", width=self._f(2))
        
        # Label underneath
        if label:
            font = self.get_font(11, bold=True)
            lines = label.split("\n")
            line_height = self._f(14)
            label_start_y = foot_y + self._f(8)
            for i, line in enumerate(lines):
                cur_y = label_start_y + i * line_height
                try:
                    left, top, right, bottom = font.getbbox(line)
                    tw = right - left
                except Exception:
                    tw = len(line) * self._f(6)
                self.draw.text((cx - tw / 2, cur_y), line, fill="#000000", font=font)

    def draw_text(self, x, y, text, font_size=11, bold=False, fill="#000000", align="center"):
        font = self.get_font(font_size, bold=bold)
        lines = text.split("\n")
        line_height = self._f(font_size * 1.35)
        for i, line in enumerate(lines):
            cur_y = self._f(y) + i * line_height
            try:
                left, top, right, bottom = font.getbbox(line)
                tw = right - left
            except Exception:
                tw = len(line) * self._f(font_size * 0.5)
            if align == "center":
                cur_x = self._f(x) - tw / 2
            elif align == "left":
                cur_x = self._f(x)
            else:
                cur_x = self._f(x) - tw
            self.draw.text((cur_x, cur_y), line, fill=fill, font=font)

    def draw_start_node(self, x, y, r=12):
        sx, sy, sr = self._f(x), self._f(y), self._f(r)
        self.draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill="#000000", outline="#000000")

    def draw_end_node(self, x, y, r=12):
        sx, sy, sr = self._f(x), self._f(y), self._f(r)
        self.draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill="#FFFFFF", outline="#000000", width=self._f(2))
        inner_r = max(1, int(sr * 0.55))
        self.draw.ellipse([sx - inner_r, sy - inner_r, sx + inner_r, sy + inner_r], fill="#000000", outline="#000000")

    def draw_box(self, x, y, w, h, label="", fill="#FFFFFF", stroke="#000000", stroke_width=1.5, radius=6, font_size=10, font_color="#000000", bold=False, align="center"):
        sx, sy, sw, sh = self._f(x), self._f(y), self._f(w), self._f(h)
        rad = self._f(radius)
        swidth = max(1, self._f(stroke_width))
        
        self.draw.rounded_rectangle([sx, sy, sx + sw, sy + sh], radius=rad, fill=fill, outline=stroke, width=swidth)
        
        if label:
            font = self.get_font(font_size, bold=bold)
            lines = label.split("\n")
            line_height = self._f(font_size * 1.35)
            total_text_h = len(lines) * line_height
            start_y = sy + (sh - total_text_h) / 2
            
            for i, line in enumerate(lines):
                cur_y = start_y + i * line_height
                try:
                    left, top, right, bottom = font.getbbox(line)
                    tw = right - left
                except Exception:
                    tw = len(line) * self._f(font_size * 0.5)
                
                if align == "center":
                    cur_x = sx + (sw - tw) / 2
                elif align == "left":
                    cur_x = sx + self._f(10)
                else:
                    cur_x = sx + sw - tw - self._f(10)
                
                self.draw.text((cur_x, cur_y), line, fill=font_color, font=font)

    def draw_ellipse(self, x, y, w, h, label="", fill="#FFFFFF", stroke="#000000", stroke_width=1.5, font_size=10, font_color="#000000"):
        sx, sy, sw, sh = self._f(x), self._f(y), self._f(w), self._f(h)
        swidth = max(1, self._f(stroke_width))
        self.draw.ellipse([sx, sy, sx + sw, sy + sh], fill=fill, outline=stroke, width=swidth)
        if label:
            font = self.get_font(font_size)
            lines = label.split("\n")
            line_height = self._f(font_size * 1.35)
            total_text_h = len(lines) * line_height
            start_y = sy + (sh - total_text_h) / 2
            for i, line in enumerate(lines):
                cur_y = start_y + i * line_height
                try:
                    left, top, right, bottom = font.getbbox(line)
                    tw = right - left
                except Exception:
                    tw = len(line) * self._f(font_size * 0.5)
                cur_x = sx + (sw - tw) / 2
                self.draw.text((cur_x, cur_y), line, fill=font_color, font=font)

    def draw_diamond(self, x, y, w, h, label="", fill="#FFFFFF", stroke="#000000", stroke_width=1.5, font_size=9.5):
        sx, sy, sw, sh = self._f(x), self._f(y), self._f(w), self._f(h)
        pts = [
            (sx + sw / 2, sy),
            (sx + sw, sy + sh / 2),
            (sx + sw / 2, sy + sh),
            (sx, sy + sh / 2)
        ]
        self.draw.polygon(pts, fill=fill, outline=stroke)
        if stroke_width > 1:
            self.draw.line(pts + [pts[0]], fill=stroke, width=max(1, self._f(stroke_width)))
        if label:
            font = self.get_font(font_size)
            lines = label.split("\n")
            line_height = self._f(font_size * 1.3)
            start_y = sy + (sh - len(lines) * line_height) / 2
            for i, line in enumerate(lines):
                cur_y = start_y + i * line_height
                try:
                    left, top, right, bottom = font.getbbox(line)
                    tw = right - left
                except Exception:
                    tw = len(line) * self._f(font_size * 0.5)
                cur_x = sx + (sw - tw) / 2
                self.draw.text((cur_x, cur_y), line, fill="#000000", font=font)

    def draw_cylinder(self, x, y, w, h, label="", fill="#FFFFFF", stroke="#000000", stroke_width=1.5, font_size=10):
        sx, sy, sw, sh = self._f(x), self._f(y), self._f(w), self._f(h)
        eh = self._f(14)
        swidth = max(1, self._f(stroke_width))
        self.draw.rectangle([sx, sy + eh / 2, sx + sw, sy + sh - eh / 2], fill=fill, outline=None)
        self.draw.line([(sx, sy + eh / 2), (sx, sy + sh - eh / 2)], fill=stroke, width=swidth)
        self.draw.line([(sx + sw, sy + eh / 2), (sx + sw, sy + sh - eh / 2)], fill=stroke, width=swidth)
        self.draw.ellipse([sx, sy + sh - eh, sx + sw, sy + sh], fill=fill, outline=stroke, width=swidth)
        self.draw.ellipse([sx, sy, sx + sw, sy + eh], fill="#FFFFFF", outline=stroke, width=swidth)
        
        if label:
            font = self.get_font(font_size, bold=True)
            lines = label.split("\n")
            line_height = self._f(font_size * 1.35)
            start_y = sy + eh + (sh - eh - len(lines) * line_height) / 2
            for i, line in enumerate(lines):
                cur_y = start_y + i * line_height
                try:
                    left, top, right, bottom = font.getbbox(line)
                    tw = right - left
                except Exception:
                    tw = len(line) * self._f(font_size * 0.5)
                cur_x = sx + (sw - tw) / 2
                self.draw.text((cur_x, cur_y), line, fill="#000000", font=font)

    def draw_arrow(self, x1, y1, x2, y2, label="", color="#000000", stroke_width=1.5, dashed=False):
        sx1, sy1, sx2, sy2 = self._f(x1), self._f(y1), self._f(x2), self._f(y2)
        swidth = max(1, self._f(stroke_width))
        
        if dashed:
            dash_len = self._f(6)
            gap_len = self._f(4)
            dx = sx2 - sx1
            dy = sy2 - sy1
            dist = (dx*dx + dy*dy)**0.5
            if dist > 0:
                ux, uy = dx / dist, dy / dist
                curr = 0
                while curr < dist:
                    seg_end = min(curr + dash_len, dist)
                    self.draw.line([(sx1 + ux * curr, sy1 + uy * curr), (sx1 + ux * seg_end, sy1 + uy * seg_end)], fill=color, width=swidth)
                    curr += dash_len + gap_len
        else:
            self.draw.line([(sx1, sy1), (sx2, sy2)], fill=color, width=swidth)

        # Arrowhead
        dx = sx2 - sx1
        dy = sy2 - sy1
        dist = (dx*dx + dy*dy)**0.5
        if dist > 0:
            ux, uy = dx / dist, dy / dist
            arrow_len = self._f(8)
            arrow_w = self._f(5)
            px = -uy * arrow_w
            py = ux * arrow_w
            tip = (sx2, sy2)
            b1 = (sx2 - ux * arrow_len + px, sy2 - uy * arrow_len + py)
            b2 = (sx2 - ux * arrow_len - px, sy2 - uy * arrow_len - py)
            if dashed:
                self.draw.line([b1, tip], fill=color, width=swidth)
                self.draw.line([b2, tip], fill=color, width=swidth)
            else:
                self.draw.polygon([tip, b1, b2], fill=color)

        if label:
            font = self.get_font(9.5)
            mx = (sx1 + sx2) / 2
            my = (sy1 + sy2) / 2 - self._f(11)
            try:
                left, top, right, bottom = font.getbbox(label)
                tw = right - left
            except Exception:
                tw = len(label) * self._f(5)
            # Mask rectangle for clean background
            self.draw.rectangle([mx - tw/2 - self._f(3), my - self._f(2), mx + tw/2 + self._f(3), my + self._f(13)], fill="#FFFFFF")
            self.draw.text((mx - tw / 2, my), label, fill="#000000", font=font)

    def draw_polyline_arrow(self, points, label="", color="#000000", stroke_width=1.5, dashed=False, label_pos=None):
        scaled_pts = [(self._f(px), self._f(py)) for px, py in points]
        swidth = max(1, self._f(stroke_width))
        
        for i in range(len(scaled_pts) - 1):
            p1 = scaled_pts[i]
            p2 = scaled_pts[i + 1]
            if dashed:
                dash_len = self._f(6)
                gap_len = self._f(4)
                dx = p2[0] - p1[0]
                dy = p2[1] - p1[1]
                dist = (dx*dx + dy*dy)**0.5
                if dist > 0:
                    ux, uy = dx / dist, dy / dist
                    curr = 0
                    while curr < dist:
                        seg_end = min(curr + dash_len, dist)
                        self.draw.line([(p1[0] + ux * curr, p1[1] + uy * curr), (p1[0] + ux * seg_end, p1[1] + uy * seg_end)], fill=color, width=swidth)
                        curr += dash_len + gap_len
            else:
                self.draw.line([p1, p2], fill=color, width=swidth)
            
        # Arrowhead on last segment
        p1 = scaled_pts[-2]
        p2 = scaled_pts[-1]
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        dist = (dx*dx + dy*dy)**0.5
        if dist > 0:
            ux, uy = dx / dist, dy / dist
            arrow_len = self._f(8)
            arrow_w = self._f(5)
            px = -uy * arrow_w
            py = ux * arrow_w
            tip = p2
            b1 = (p2[0] - ux * arrow_len + px, p2[1] - uy * arrow_len + py)
            b2 = (p2[0] - ux * arrow_len - px, p2[1] - uy * arrow_len - py)
            if dashed:
                self.draw.line([b1, tip], fill=color, width=swidth)
                self.draw.line([b2, tip], fill=color, width=swidth)
            else:
                self.draw.polygon([tip, b1, b2], fill=color)
            
        if label and len(points) >= 2:
            if label_pos:
                mx = self._f(label_pos[0])
                my = self._f(label_pos[1])
            else:
                # Find longest segment to place label cleanly
                best_len = -1
                best_seg = (points[0], points[1])
                for i in range(len(points) - 1):
                    seg_dx = points[i+1][0] - points[i][0]
                    seg_dy = points[i+1][1] - points[i][1]
                    seg_d = (seg_dx*seg_dx + seg_dy*seg_dy)**0.5
                    if seg_d > best_len:
                        best_len = seg_d
                        best_seg = (points[i], points[i+1])
                
                sp1, sp2 = best_seg
                mx = self._f((sp1[0] + sp2[0]) / 2)
                my = self._f((sp1[1] + sp2[1]) / 2) - self._f(12)

            font = self.get_font(9.5)
            try:
                left, top, right, bottom = font.getbbox(label)
                tw = right - left
            except Exception:
                tw = len(label) * self._f(5)
            self.draw.rectangle([mx - tw/2 - self._f(3), my - self._f(2), mx + tw/2 + self._f(3), my + self._f(13)], fill="#FFFFFF")
            self.draw.text((mx - tw/2, my), label, fill="#000000", font=font)

    def draw_swimlane(self, x, y, w, h, title, fill="#FFFFFF", header_fill="#FFFFFF"):
        sx, sy, sw, sh = self._f(x), self._f(y), self._f(w), self._f(h)
        hh = self._f(32)
        swidth = max(1, self._f(1.5))
        # Total lane
        self.draw.rectangle([sx, sy, sx + sw, sy + sh], fill=fill, outline="#000000", width=swidth)
        # Header bar
        self.draw.rectangle([sx, sy, sx + sw, sy + hh], fill=header_fill, outline="#000000", width=swidth)
        font = self.get_font(11, bold=True)
        try:
            left, top, right, bottom = font.getbbox(title)
            tw = right - left
        except Exception:
            tw = len(title) * self._f(6)
        self.draw.text((sx + (sw - tw) / 2, sy + self._f(7)), title, fill="#000000", font=font)

    def save(self, filepath):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        self.img.save(filepath, "PNG", dpi=(150, 150))

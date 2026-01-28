import cv2
import numpy as np

class Lens:
    def __init__(self, name, position_x):
        self.name = name
        self.f = 0.0 # Default undefined
        self.pos_x = position_x
        
    def set_focal_length(self, f):
        self.f = f
        
    def draw(self, canvas, axis_y):
        """
        Draws the lens on the visualization canvas.
        Shape depends on f:
         - Positive f: Convex (double convex look) ()
         - Negative f: Concave (double concave look) )(
         - Infinity/Zero Power: Vertical line |
        """
        h, w = canvas.shape[:2]
        
        cx = self.pos_x
        cy = axis_y
        height = 80 # Height of lens symbol
        
        color = (200, 200, 200)
        thickness = 2
        
        # Determine curvature based on f
        # Small f = high curvature. Large f = flat.
        # We treat f=0 (from slider) as infinite power (should not happen with our optics logic clamp)
        # OR we treat slider 0 as "No Lens" which is f=infinity.
        # In optics.py we treated slider abs<10 as infinity.
        
        is_planar = False
        if abs(self.f) < 10:
             is_planar = True
        
        if is_planar:
            # Draw straight vertical line representing glass plate / no power
            cv2.line(canvas, (cx, cy - height//2), (cx, cy + height//2), color, thickness)
        else:
            # Draw curves
            # Strength of curve
            curvature = min(20, 1000.0 / abs(self.f)) # Cap curvature for visuals
            
            pts_left = []
            pts_right = []
            
            steps = 20
            for i in range(steps + 1):
                t = i / steps # 0 to 1
                y = cy - height//2 + t * height
                
                # Parabolic offset
                # Normalized y from -1 to 1
                ny = (t - 0.5) * 2
                x_offset = curvature * (1 - ny**2)
                
                if self.f > 0: # Convex ()
                    pts_left.append((cx - x_offset, y))
                    pts_right.append((cx + x_offset, y))
                else: # Concave )(
                    # For concave, tips are wider than center.
                    # x_offset is max at center.
                    # We want tips to be constant width? Or center to start thin?
                    # Let's do: Center is cx. Tips are cx +/- curvature.
                    # Curve goes inwards.
                    x_inward = curvature * (ny**2)
                    pts_left.append((cx - 5 - x_inward, y)) # Fixed width base + curve
                    pts_right.append((cx + 5 + x_inward, y))

            pts_left = np.array(pts_left, dtype=np.int32)
            pts_right = np.array(pts_right, dtype=np.int32)
            
            # Draw curves
            cv2.polylines(canvas, [pts_left], False, color, thickness)
            cv2.polylines(canvas, [pts_right], False, color, thickness)
            
            # Close the shape? Lens usually closed.
            cv2.line(canvas, tuple(pts_left[0]), tuple(pts_right[0]), color, 1)
            cv2.line(canvas, tuple(pts_left[-1]), tuple(pts_right[-1]), color, 1)

        # Label
        text = f"{self.name}: {self.f}mm"
        if is_planar:
            text = f"{self.name}: FLAY (inf)"
        
        cv2.putText(canvas, text, (cx - 40, cy + height//2 + 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

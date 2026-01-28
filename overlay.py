import cv2
import numpy as np
from optics import get_focus_status

def draw_overlay(frame, lenses, f_eff, f_target):
    """
    Draws the optical bench visualization overlay on top of the frame.
    Typically, we might want to append this to the bottom or draw purely on top.
    To ensure visibility, we'll draw on a semi-transparent background box 
    or just append a footer if user prefers "on top". 
    Actually, overlaying on the video is cool.
    """
    h, w = frame.shape[:2]
    
    # Define area for optical bench (bottom 1/3 defined?)
    # or centered.
    # Let's draw it at the bottom.
    
    bench_y = h - 100
    
    # Draw Axis
    cv2.line(frame, (50, bench_y), (w - 50, bench_y), (100, 100, 100), 1)
    
    # Draw Lenses
    for lens in lenses:
        lens.draw(frame, bench_y)
        
    # Draw Rays (Simplified) - Just converging lines from left to right?
    # Maybe too complex for simple overlay, let's stick to text status.
    
    # Overlay Info Box
    status_text, status_color = get_focus_status(f_eff, f_target)
    
    info_x = 20
    info_y = 40
    line_height = 25
    
    # Backdrop for text
    cv2.rectangle(frame, (10, 10), (300, 150), (0, 0, 0), -1) # Black box
    
    cv2.putText(frame, "OPTICAL SIMULATION", (info_x, info_y), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    cv2.putText(frame, f"F_eff: {f_eff:.1f} mm", (info_x, info_y + line_height), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
    
    cv2.putText(frame, f"Target: {f_target:.1f} mm", (info_x, info_y + line_height*2), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)
    
    cv2.putText(frame, f"Status: {status_text}", (info_x, info_y + line_height*3), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, status_color, 2)
                
    cv2.putText(frame, "Controls: Sliders window", (info_x, info_y + line_height*4), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)
    
    return frame

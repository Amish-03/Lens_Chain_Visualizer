import cv2
import numpy as np
from optics import calculate_effective_focal_length, apply_lens_effect
from lens import Lens
from overlay import draw_overlay

def nothing(x):
    pass

def main():
    # Initialize Camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    # Window
    cv2.namedWindow('Lens Simulation')
    cv2.namedWindow('Controls')
    
    # Create Trackbars
    # Range -300 to 300. Trackbars only support positive.
    # We will map 0-600 to -300 to 300. 
    # To make initial state "Hypermetropia corrected":
    # Let's say Target is 100mm.
    # We want default effective = 100mm.
    # Maybe f1=200, f2=200, f3=inf (0 power)? 
    # 1/200 + 1/200 = 2/200 = 1/100.
    
    default_slider = 300 + 100 # Represents +100mm
    # Actually wait. Mapping: Val - 300 = f.
    # If val=400, f=100.
    # If val=300, f=0 (which we treat as infinity/planar).
    
    cv2.createTrackbar('Lens 1 F', 'Controls', 300 + 150, 600, nothing) # Start at +150
    cv2.createTrackbar('Lens 2 F', 'Controls', 300 + 300, 600, nothing) # Start at +300
    cv2.createTrackbar('Lens 3 F', 'Controls', 300 + 0, 600, nothing)   # Start at 0 (Planar)
    
    # Define Target F (The "Retina" distance)
    # Let's pick 100mm as the arbitrary target for "Perfect Focus"
    # Why 100? It's a nice round number in our range.
    f_target = 100.0 
    
    # Layout Lenses for visualization
    # We map x-positions based on frame width roughly
    # We'll update positions in loop if width changes, or fix them.
    # Fixed for now.
    lenses = [Lens("L1", 200), Lens("L2", 320), Lens("L3", 440)]
    
    print("Starting simulation. Press 'q' to exit.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Get Frame Size for UI layout
        h, w = frame.shape[:2]
        
        # Update Lens Positions (Responsive UI)
        center_x = w // 2
        lenses[0].pos_x = center_x - 120
        lenses[1].pos_x = center_x
        lenses[2].pos_x = center_x + 120
        
        # Read Sliders
        v1 = cv2.getTrackbarPos('Lens 1 F', 'Controls')
        v2 = cv2.getTrackbarPos('Lens 2 F', 'Controls')
        v3 = cv2.getTrackbarPos('Lens 3 F', 'Controls')
        
        # Determine f values
        # Mapping: 0..600 -> -300..300
        # Exception: We treat value 300 (f=0) as "Planar / Inf" in optics.py logic 
        # (checks if abs(f)<10).
        f1 = v1 - 300
        f2 = v2 - 300
        f3 = v3 - 300
        
        # Update Lens Objects
        lenses[0].set_focal_length(f1)
        lenses[1].set_focal_length(f2)
        lenses[2].set_focal_length(f3)
        
        # Calculate Effective F
        f_eff = calculate_effective_focal_length(f1, f2, f3)
        
        # Apply Optical Effects
        processed_frame = apply_lens_effect(frame, f_eff, f_target)
        
        # Draw Overlay
        display_frame = draw_overlay(processed_frame, lenses, f_eff, f_target)
        
        cv2.imshow('Lens Simulation', display_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

import cv2
import numpy as np

def calculate_effective_focal_length(f1, f2, f3):
    """
    Computes effective focal length using the thin lens approximation in contact:
    1/f_eff = 1/f1 + 1/f2 + 1/f3
    
    Handles f=0 (infinite power, theoretically impossible for single lens but handled as extreme)
    or f=infinity (power=0) via large numbers.
    
    Args:
        f1, f2, f3 (float): Focal lengths in arbitrary units (e.g., mm). 
                            0 denotes a placeholder for infinite power (not allowed usually),
                            but here we might treat very large input as infinity.
                            We assume input is never exactly 0 from sliders (range usually excludes 0, or we clamp).
    
    Returns:
        float: Effective focal length.
    """
    # Safe inverse: treat 0 as epsilon to avoid div by zero if sliders allow it.
    # Actually, sliders usually give an int. We should avoid 0.
    
    p1 = 1.0 / f1 if abs(f1) > 1e-5 else 0 # If f is super small, power is huge. 
                                           # If we want to support planar (f=inf), p=0.
                                           # Our sliders will likely go -300 to 300. 
                                           # We need a way to represent "0 power" (f=inf).
                                           # Usually optometry uses Diopters (D=1000/f_mm).
                                           # But simplified: just sum 1/f.
    
    p2 = 1.0 / f2 if abs(f2) > 1e-5 else 0
    p3 = 1.0 / f3 if abs(f3) > 1e-5 else 0
    
    # If using direct f values, 0 usually implies "no lens" ?? 
    # No, f=infinity is no lens. f=0 is infinite power.
    # Code strategy: Sliders control 'f'. 
    # Issue: Continuous slider from -300 to +300 crosses 0.
    # At 0, power is infinite. This is bad for simulation.
    # PROPOSAL: Sliders control POWER (Diopters) instead of f, or we clamp f to avoid 0.
    # Since prompt asks for "sliders for f1, f2, f3", we'll implement that but with a "dead zone" or clamp near 0.
    # Or, perhaps 0 on the slider implies "glass plate" (f=inf)? 
    # That would be intuitive for a UI, but mathematically 0 is f=0.
    # Let's check prompt: "Real-time sliders for f1, f2, f3 (range: -300 mm to +300 mm)"
    # If slider is 0, we should probably treat it as "Neutral / No Lens" for usability, 
    # OR clamp it to a small epsilon. 
    # Let's interpret 0 as "Infinite focal length (Power 0)" for better UX, 
    # because typically a "0" setting on a tool means "off".
    
    p1 = 1.0 / f1 if abs(f1) >= 10 else 0 # treating anything between -10 and 10 as "planar" (no power)
    p2 = 1.0 / f2 if abs(f2) >= 10 else 0
    p3 = 1.0 / f3 if abs(f3) >= 10 else 0
    
    P_total = p1 + p2 + p3
    
    if abs(P_total) < 1e-5:
        return float('inf')
    
    return 1.0 / P_total

def apply_lens_effect(frame, f_eff, f_target):
    """
    Applies zoom and blur based on the difference between f_eff and f_target.
    
    Args:
        frame (numpy.ndarray): Input image.
        f_eff (float): Current system focal length.
        f_target (float): Ideal focal length for creating a focused image on the sensor.
        
    Returns:
        numpy.ndarray: Processed image.
    """
    h, w = frame.shape[:2]
    
    # --- 1. Blur (Defocus) ---
    # Heuristic: Blur is proportional to power difference |1/f_eff - 1/f_target|
    # Power difference in Diopters if units were meters.
    
    target_power = 1.0 / f_target if f_target != 0 else 0
    current_power = 1.0 / f_eff if f_eff != 0 else 0
    
    power_diff = abs(current_power - target_power)
    
    # Scaling factor for visual effect
    # e.g. difference of 0.01 (1/100mm vs 1/infinity) -> strong blur
    blur_scale = 5000.0 # Tuning constant
    k_size = int(power_diff * blur_scale)
    
    # Ensure odd kernel size
    if k_size % 2 == 0:
        k_size += 1
    k_size = max(1, min(k_size, 51)) # Cap blur to reasonable max 51
    
    blurred_frame = frame
    if k_size > 1:
        blurred_frame = cv2.GaussianBlur(frame, (k_size, k_size), 0)
        
    # --- 2. Zoom (Magnification) ---
    # M ~ f_eff / f_target
    # If f_eff > f_target, we zoom IN (image gets larger).
    # If f_eff < f_target, we zoom OUT (image gets smaller).
    # We need to handle sign. Negative focal length (virtual image) is tricky to visualize straightforwardly 
    # as "projected on sensor" without ray tracing.
    # We will just take magnitude for scaling simple visualization, or invert if negative?
    # Let's use magnitude for scale to avoid flipping image upside down continuously which might be disorienting.
    
    # If f_eff is infinite (power 0), scale is 1 (or dependent on assumption).
    # Let's restrict scale to safe limits.
    
    if f_eff == float('inf'):
        scale = 1.0
    else:
        # Avoid div by zero / extreme scales
        # Base scale logic:
        # If f_eff = f_target, scale = 1.
        scale = abs(f_eff) / abs(f_target)
        
    # Cap scale
    scale = max(0.1, min(scale, 5.0))
    
    # Perform Resize
    center_x, center_y = w // 2, h // 2
    
    # Resize
    new_w, new_h = int(w * scale), int(h * scale)
    resized = cv2.resize(blurred_frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    
    # Crop or Pad to match original size
    # Create black canvas
    output = np.zeros_like(frame)
    
    if scale >= 1.0:
        # Crop center
        x_start = (new_w - w) // 2
        y_start = (new_h - h) // 2
        output = resized[y_start:y_start+h, x_start:x_start+w]
    else:
        # Pad center
        x_start = (w - new_w) // 2
        y_start = (h - new_h) // 2
        output[y_start:y_start+new_h, x_start:x_start+new_w] = resized
        
    return output

def get_focus_status(f_eff, f_target, threshold_power=0.001):
    """
    Returns string status of focus.
    Using Power comparison (1/f) is more robust than f comparison given ranges.
    """
    p_eff = 1.0 / f_eff if f_eff != 0 else 0
    p_tar = 1.0 / f_target if f_target != 0 else 0
    
    diff = p_eff - p_tar
    
    if abs(diff) < threshold_power: # Roughly matches within reasonable tolerance
        return "IN FOCUS", (0, 255, 0) # Green
    elif diff > 0:
        # More power than needed (Converges too soon) -> Myopic relative to sensor
        return "OVER-CORRECTED (Short)", (0, 0, 255) # Red
    else:
        # Less power than needed (Converges too late or diverges) -> Hyperopic
        return "UNDER-CORRECTED (Long)", (0, 255, 255) # Yellow

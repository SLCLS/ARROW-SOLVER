import cv2
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import screen_map

def generate_perfect_templates():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(script_dir, "calibration", "screen.png")
    img = cv2.imread(mg_path, cv2.IMREAD_GRAYSCALE)

    if img is None:
        raise FileNotFoundError(f"Could not load master screenshot at {img_path}")
    
    template_source = {
        1: (-3, 0),  
        2: (-2, 0),  
        3: (-3, 1),   
        4: (-1, 3),   
        5: (-3, 2),   
        6: (-2, 1)
    }

    out_dir = os.path.join(script_diir, "templates")
    os.makedirs(out_dir, exist_ok=True)

    box_size = 80
    half = box_size // 2

    print("--- Auto-Generating 1:1 Pixel Templates ---")
    for val, coord in template_source.items():
        x, y = screen_map[coord]
        crop = img[y - half : y + half, x - half : x + half]
        
        out_file = os.path.join(out_dir, f"{val}.png")
        cv2.imwrite(out_file, crop)
        print(f"Saved {val}.PNG extracted directly from {coord}")
        
    print("\n[SUCCESS] Overwrote old templates. Scale mismatch eliminated.")

if __name__ == "__main__":
    generate_perfect_templates()
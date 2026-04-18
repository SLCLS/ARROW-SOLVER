import cv2
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import screen_map

class BoardScanner:
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.templates = {}
        self._load_templates()

        self.crop_size = 180 

    def _load_templates(self):
        """Loads templates and converts them to pure edge maps."""
        for i in range(1, 7):
            path = os.path.join(self.script_dir, "templates", f"{i}.PNG")
            tmpl = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            if tmpl is None:
                raise FileNotFoundError(f"Missing template: {path}")

            edges = cv2.Canny(tmpl, 50, 150)
            self.templates[i] = edges

    def scan(self, image_path):
        """Scans the board and returns a dictionary of {(q, r): value}"""

        img_color = cv2.imread(image_path)
        img_gray = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)
        
        if img_gray is None:
            raise FileNotFoundError(f"Could not load screenshot at {image_path}")

        board_state = {}
        half_c = self.crop_size // 2

        for coord, (x, y) in screen_map.items():

            y1 = max(0, y - half_c)
            y2 = min(img_gray.shape[0], y + half_c)
            x1 = max(0, x - half_c)
            x2 = min(img_gray.shape[1], x + half_c)
            
            roi = img_gray[y1:y2, x1:x2]
            edges_roi = cv2.Canny(roi, 50, 150)
            
            best_match_val = -1
            best_match_score = -1
            
            for val, tmpl_edges in self.templates.items():

                if tmpl_edges.shape[0] > edges_roi.shape[0] or tmpl_edges.shape[1] > edges_roi.shape[1]:
                    continue

                res = cv2.matchTemplate(edges_roi, tmpl_edges, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, _ = cv2.minMaxLoc(res)
                
                if max_val > best_match_score:
                    best_match_score = max_val
                    best_match_val = val
                    
            board_state[coord] = best_match_val
            
            cv2.putText(img_color, f"{coord[0]},{coord[1]}", (x - 50, y - 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            
            cv2.putText(img_color, str(best_match_val), (x - 20, y + 20), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.8, (0, 255, 0), 4)

        debug_out = os.path.join(self.script_dir, "debug_board_scanned.png")
        cv2.imwrite(debug_out, img_color)
        print(f"\n[!] Visual Debug Image Saved to: {debug_out}")
            
        return board_state

if __name__ == "__main__":
    scanner = BoardScanner()
    img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "calibration", "screen.png")
    
    try:
        state = scanner.scan(img_path)
        print(">>> SCAN COMPLETE <<<")
        for coord, val in state.items():
            print(f"Hex {coord} -> Value: {val}")
            
    except Exception as e:
        print(f"Error: {e}")
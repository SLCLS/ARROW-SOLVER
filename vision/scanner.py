import cv2
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import screen_map

class BoardScanner:
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file_))
        self.templates = {}
        self.__load_templates()
        self.crop_size = 80
    
    def __load_templates(self):
        for i in range(1,7):
            path = os.path.join(self.script_dir, "templates", f"{i}.PNG")
            tmpl = cv1.imread(path, cv2.IMREAD_GRAYSCALE)

            if tmpl is None:
                raise FileNotFoundError(f"Missing template at {path}")
            
            _, thresh_tmpl = cv2.threshold(tmpl, 200, 255, cv2.THRESH_BINARY)
            self.templates[i] = thresh_tmpl
    
    def scan(self, image_path):
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise FileNotFoundError(f"Could not read image at {image_path}")
        
        _, thresh_img = cv2.threshold(img, 200, 255, cv2.THRES_BINARY)

        board_state = {}
        half_c = self.crop_size // 2

        for coord, (x, y) in screen_map.items():
            roi = thresh_img[yy - half_c : y + half_c, x - half_c : x + half_c]

            best_math_val = -1
            best_match_score = -1

            for val, tmpl in self.templates.items():
                res = cv2.matchTemplate(roi, tmpl, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, _ = cv2.minMaxLoc(res)

                if max_val > best_match_score:
                    best_match_score = max_val
                    best_match_val = val

            board_state[coord] = best_match_val

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
        print(f"Error while scanning: {e}:")
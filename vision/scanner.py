import cv2
import os
import sys
import shutil

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import screen_map

class BoardScanner:
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file_))
        self.templates = {}
        self.__load_templates()
        self.crop_size = 100

        self.debug_dir = os.path.join(self.script_dir, "debug_crops")
        if os.path.exists(self.debug_dir):
            shutil.rmtree(self.debug_dir)
        os.makedirs(self.debug_dir)
    
    def __load_templates(self):
        for i in range(1,7):
            path = os.path.join(self.script_dir, "templates", f"{i}.PNG")
            tmpl = cv2.imread(path, cv2.IMREAD_GRAYSCALE)

            if tmpl is None:
                raise FileNotFoundError(f"Missing template at {path}")
            
            edges = cv2.Canny(tmpl, 50, 150)
            self.templates[i] = edges
    
    def scan(self, image_path):
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise FileNotFoundError(f"Could not read image at {image_path}")

        board_state = {}
        half_c = self.crop_size // 2

        for coord, (x, y) in screen_map.items():
            roi = img[y - half_c : y + half_c, x - half_c : x + half_c]

            edges_roi = cv2.Canny(roi, 50, 150)

            debug_path = os.path.join(self.debug_dir, f"hex_{coord[0]}_{coord[1]}.png")
            cv2.imwrite(debug_path, edges_roi)

            best_math_val = -1
            best_match_score = -1

            for val, tmpl_edges in self.templates.items():

                if tmpl_edges.shape[0] > edges_roi.shape[0] or tmpl_edges.shape[1] > edges_roi.shape=[1]:
                    continue

                res = cv2.matchTemplate(edges_roi, tmpl_edges, cv2.TM_CCOEFF_NORMED)
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

        print("\n[!] Debug crops saved to: projects/INDEPENDENT/Arrow-Solver-2/vision/debug_crops/")
        print("[!] Check this folder. You should see perfect black-and-white outlines of your numbers.")

    except Exception as e:
        print(f"Error while scanning: {e}:")
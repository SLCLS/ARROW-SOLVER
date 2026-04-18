import cv2
import os

class ScreenCalibrator:
    def __init__(self, image_path):
        self.img = cv2.imread(image_path)
        if self.img is None:
            raise FileNotFoundError(f"Could not load image at {image_path}")
            
        self.clone = self.img.copy()
        self.clicks = []
        self.radius = 3
        
    def _click_event(self, event, x, y, flags, params):
        """Records mouse clicks on the image."""
        if event == cv2.EVENT_LBUTTONDOWN:
            self.clicks.append((x, y))
            cv2.circle(self.img, (x, y), 5, (0, 0, 255), -1)
            cv2.imshow("Calibrator", self.img)
            
            if len(self.clicks) == 2:
                self._calculate_grid()

    def _calculate_grid(self):
        """
        Calculates a pointy-topped hex grid using Center and Upper-Right coordinates.
        """
        center_x, center_y = self.clicks[0]
        top_right_x, top_right_y = self.clicks[1]

        W = top_right_x - center_x
        half_H = center_y - top_right_y
        H = half_H * 2
        
        mapping = {}
        print("\n--- Generating Coordinate Mapping ---")

        for q in range(-self.radius, self.radius + 1):
            for r in range(-self.radius, self.radius + 1):
                if abs(q + r) <= self.radius:

                    px = int(center_x + q * W)
                    py = int(center_y + q * half_H + r * H)
                    
                    mapping[(q, r)] = (px, py)

                    cv2.circle(self.img, (px, py), 10, (0, 255, 0), -1)
                    cv2.putText(self.img, f"{q},{r}", (px - 15, py - 15), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

        cv2.imshow("Calibrator", self.img)
        print("Grid mapped! If the green dots align with the tiles, save this dictionary:")
        print("screen_map = {")
        for k, v in mapping.items():
            print(f"    {k}: {v},")
        print("}")

    def run(self):
        print("1. Click the exact center of the MIDDLE tile (0,0).")
        print("2. Click the exact center of the UPPER-RIGHT tile (1,-1).")
        print("Press any key to close the window after calibration.")
        

        cv2.namedWindow("Calibrator", cv2.WINDOW_NORMAL)
        
        h, w = self.img.shape[:2]
        cv2.resizeWindow("Calibrator", int(w * 0.3), int(h * 0.3))
        
        cv2.imshow("Calibrator", self.img)
        cv2.setMouseCallback("Calibrator", self._click_event)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(script_dir, "calibration", "screen.png")
    
    print(f"Loading image from: {img_path}")
    
    calibrator = ScreenCalibrator(img_path)
    calibrator.run()
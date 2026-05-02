import cv2
import math

class ScreenCalibrator:
    def __init__(self, image_path):
        self.img = cv2.imread(image_path)

        if self.img is None:
            raise FileNotFoundError(f"Image not found at path: {image_path}"    )
        
        self.clone = self.img.copy()
        self.clicks = []
        self.radius = 3

    def _click_event(self, event, x, y, flags, params):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.clicks.append((x, y))
            cv2.circle(self.img, (x, y), 5, (0, 255, 0), -1 )
            cv2.imshow("Calibration", self.img)

            if len(self.clicks) == 2:
                self._calculate_grid()
    
    def _calculate_grid(self):
        center_x, center_y = self.clicks[0]
        right_x, right_y = self.clicks[1]

        W = math.sqrt((right_x - center_x)**2 + (right_y - center_y)**2)
        H = W * (math.sqrt(3) / 2)

        mapping = {}
        print("\n--- Generating Coordinate Mapping ---")
    
        for q in range(-self.radius, self.radius + 1):
            for r in range(-self.radius, self.radius + 1):
                px = int(center_x + W * (q + r / 2))
                py = int(center_y + H * r)

                mapping[(q, r)] = (px, py)

                cv2.circle(self.img, (px, py), 10, (0, 255, 0), -1)
                cv2.putText(self.img, f"{q},{r}", (px - 15, py - 15),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
                
        cv2.imgshow("Calibrator", self.img)
        print("Grid mapped! If the green dots align with the tiles, save this dictionary:")
        print("screen_map = {")
        for k, v in mapping.items():
            print(f"   {k}: {v},")
        print("}")

    def run(self):
        print("1. Click the exact center of the middle tile. (0, 0)")
        print("2. Click the exact center of the tile immediately to the right (1,0).")
        print("Press any key to close after calibration, see the values on your terminal.")

        cv2.imshow("Calibrator", self.img)
        cv2.setMouseCallback("Calibrator", self._click_event)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    calibrator = ScreenCalibrator("screen.png")
    calibrator.run()
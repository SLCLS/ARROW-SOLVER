ADDED THIS:
So the tens of hours spent on testing the program against my screen dimension, cv2, adb, and scrcpy doesn't go uncounted. I documented my experimental observations throughout the program development in this file.

## 03/01/2026:

### 1. Replicated the arrow board via a structured axial coordinate.

NOTE:
Flip the puzzle visually in a way wherein the upper left side of the hexagon becomes the top part. The rows of tiles are then represented by the coordinate/variable r {stands for row} starting at r=0 at the middle-most row, decremented by 1 as it goes toward the top and incremented by 1 as it goes down. P.S. it sounds counter-intuitive since the vertical counting of the rows are negative as it goes towards the top and vice versa, but hey, it works and I added `/docs/coordinates.png` to be able to visualize this easier when running board.py. The q variable on the other hand represents the column of the tiles wherein the center-most column is represented by 0 and is incremented/decremented by 1 as it goes right/left.

DEBUGGING NOTE:
Added features one by one, first the coordinate and tiles, then the relationship with other tiles, then the 6 possible state or rotations. Tested each added features every step of the wayy. I have tested board.py and each tiles seems to be proper based on the set coordinate system. In addition, I have verified the it properly rotates up to 6 times then returns to normal. Propagation to it's neighboring tiles are also tested and everything seems to be working well. Spend sometime properly debugging this part so I can proceed with solver.py.

### 2. Tested solver.py against the simulated arrow puzzle boards.

The algorithm (not coded, but rather documented) for this is documented on this guide: https://exponential-idle-guides.netlify.app/guides/asd/ (ty to the expo idle community).

NOTE: (visualize the original arrow puzzle interface) For the initial propagation, I set it so that the lower left tile from the top row are tapped first. Once it is all propagated, I followed the standard algorithm for solving this. You may check out solver.py, I use the same letters for the program variable:

`A, B, C, D = (0, 3), (1, 2), (2, 1), (3, 0)`
`a, b, c, d = (0, -3), (1, -3), (2, -3), (3, -3)`

Wherein to solve it, I followed the documented algorithm:
    a. Tap a so that a is the same as C.
    b. Tap b and d the num­ber of times you will need to solve C.
    c. Tap a the num­ber of times you would need to solve D.
    d. If B + D is odd, tap c three times (once in Hard).

I added verbosity so I can manually verify its taps. A random puzzle board usually shows 100+ moves in average so it's just simply impractical for me to counter-check it manually one by one. But I analyzed most of the end game part, considering the proper coordinate checks, neighbor relations, and accuracy of the algorithm. Seems to be working well, proceeding to vision tomorrow morning.

ADDITIONAL TAKE-AWAY FOR IMPROVEMENT:
- 100 moves seems absurd, I'll check on how to optimize this later on.

## 03/02/2026:

Fought of some issues with android adb, numpy, and opencv all throughout the day since my bleeding edge python version is unsupported by some of the dependencies.

### 1. Added calibrate.py which functions as a helper for vision.py. It essentially identifies the proper placement of the tiles and coordinates based on the distance of the center tile. To be honest, I could've opted not to add this module entirely and rather just map the coordinates of each tile manually, but I really wanted this project to be shippable and useable for everyone. It basically we can extract the base x and y origin and the horizontal pixel spacing (represented by W). It's a regular hexagon, so the vertical spacing  is just W x {sqrt(3)/(2)}. I used it to project the exact center of all hte 37 tiles based on the 0,0 and 1,0 tile.

Testing logs:
`adb shell screencap -p /sdcard/screen.png`
`adb pull /sdcard/screen.png`

(for some reason it didn't worked)

Okay, so I kinda figured out why. I used the coordinate based interface (flat-topped hexagonal grid) to calibrate but the game UI uses the regular pointy chip like hexagon. Making some adjustments.

Results of my screen based coordinates are added on a new file at root "`config.py`" (should've probably made it a json file, but it won't be large though so I'll leave it as is.)

Also see `/vision/calibration` and `/vision/templates` (this is probably standard for all devices unless someone is tweaking the app UI).

### 2. Added the required dependencies on requirements.txt
`pip freeze > requirements.txt`

### 3. Added a scanner.py module after a long documentation and tutorial binged. For some reason though, it's really not detecting anything properly. It returns only 1, 5, and 6. Still needs a lot of debugging but i'll try to check how can I properly identify the numbers on the screen.

INSIGHTS AND CHANGES:
So I just learned that the program that I created earlier is actually acting as a pixel counter and identifying the number based on it. Unfortunately, due to the variance in the photos of the numbers that I took using a screenshot of my phone and windows snipping tool... It got messed up. So I decided to try another solution: "Canny Edge Detection".

## 05/04/2026:

### 1. Finally been able to make the computer vision module (`scanner.py`) work. I adjustedd crop_size from 100 to 180 (found this to have optimally covered all of the patterns on each number), and i removed the `/debug_crops` function after verifying that the program is stable enough. Made some changes on the dimenton as well:
```
y1 = max(0, y - half_c)
y2 = min(img_gray.shape[0], y + half_c)
x1 = max(0, x - half_c)
x2 = min(img_gray.shape[1], x + half_c)
roi = img_gray[y1:y2, x1:x2]
```

The main change however is this line:
```img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)```
to this
```
img_color = cv2.imread(image_path)
img_gray = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)
```
which rather pulls the image with color instead of just it looking at the grayscale.

NOTE: Although the CV program is working, it still only returns ~70% recognition accuracy. I have identified that initial static template I provided to feed the program introduced scaling artifacts and inconsistencies on the dimension itself which     may have contributed to some of the errors. Planning to use `adb screencap` to automatically capture a uniform image of all the tiles (then selecting one of each state).

### 2. Added `auto_template.py` that solves the exact issue that I've been encountering earlier with the inaccurate cv reading. It basically uniformly captures a uniform and perfect template of each state based on the coordinates provided. (replaced the images on `/vision/templates` already)

NOTE: All goods for the computer vision, returns the correct value of each tile 100% of the time. Also, worth noting, even if the night screen is enabled and is being fed, the program seems to still be working well enough to not return any inaccuracy or errors.

### 3. Added the ADB input output module (`adb_ctrl.py`)
super sleepy rn, i'll test it out later today.
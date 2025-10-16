import cv2
import numpy as np
import matplotlib.pyplot as plt

img = cv2.imread("0694000197.jpg", cv2.IMREAD_GRAYSCALE)


start_height, end_height = 0, 320
start_width, end_width = 155, 195

roi = img[start_height:end_height, start_width:end_width]

profile = np.mean(roi, axis=1)

gradient = np.diff(profile)

pos = np.argmin(gradient)

print(pos)

y_value = pos + start_height + 237

print(f"Line detected at Y = {y_value}")

plt.figure(figsize=(10,4))
plt.subplot(1,2,1); plt.imshow(roi, cmap="gray"); plt.axhline(pos, color="r"); plt.title("ROI with detected line")
plt.subplot(1,2,2); plt.plot(profile, label="Profile"); plt.plot(gradient, label="Gradient"); 
plt.axvline(pos, color="r", linestyle="--", label="Detected line")
plt.legend(); plt.show()

start_height2, end_height2 = 125, 135
start_width2, end_width2 = 100, 175

roi2 = img[pos + start_height2: pos + end_height2, start_width2:end_width2]

profile2 = np.mean(roi2, axis=0)

gradient2 = np.diff(profile2)

posy = np.argmax(gradient2)
print(posy)
x_value = start_width2 + posy + 3
 
print(f"Line detected at X = {x_value}")

plt.figure(figsize=(10,4))
plt.subplot(1,2,1); plt.imshow(roi2, cmap="gray"); plt.axvline(posy, color="r"); plt.title("ROI with detected line")
plt.subplot(1,2,2); plt.plot(profile2, label="Profile"); plt.plot(gradient2, label="Gradient"); 
plt.axvline(posy, color="r", linestyle="--", label="Detected line")
plt.legend(); plt.show()

start_h = y_value 
end_h = y_value + 62

start_w = x_value 
end_w = x_value + 62

image_cropped = img[start_h:end_h, start_w:end_w]
cv2.imwrite("image_cropped.jpg", image_cropped)
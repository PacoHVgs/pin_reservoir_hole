import cv2

image = cv2.imread("job10.jpg")

image_cropped = image[235:297, 70:132]
cv2.imwrite("image_cropped_grande.jpg", image_cropped)

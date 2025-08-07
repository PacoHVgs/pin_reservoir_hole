import cv2

image = cv2.imread("0694000197.jpg")

height, width = 62, 62

init_pix_height, init_pix_width = 275, 123
end_pix_height, end_pix_width = (init_pix_height + height), (init_pix_width + width)

print(end_pix_height)

image_cropped = image[init_pix_height:end_pix_height, init_pix_width:end_pix_width]
cv2.imwrite("0694000197_cropped.jpg", image_cropped)

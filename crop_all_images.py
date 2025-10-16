import cv2
import os

path = "0694000197/Complete"
new_path = "0694000197/Cropped_New"

os.makedirs(new_path, exist_ok=True)

images = os.listdir(path)

height, width = 62, 62

init_pix_height, init_pix_width = 275, 123
end_pix_height, end_pix_width = (init_pix_height + height), (init_pix_width + width)

for original_image in images:
    if "jpg" in original_image:
        original_image_path = os.path.join(path, original_image)
        new_image_path = os.path.join(new_path, original_image)
        image = cv2.imread(original_image_path)
        image_cropped = image[init_pix_height:end_pix_height, init_pix_width:end_pix_width]
        cv2.imwrite(new_image_path, image_cropped)
        print(f"Imagen {original_image} cortada")

    else:
        print(f"{original_image} no es uan imagen")



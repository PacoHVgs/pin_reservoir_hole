import cv2
import os

path = "Accord - Odissey"
new_path = "images_cropped"

os.makedirs(new_path, exist_ok=True)

images = os.listdir(path)

for original_image in images:
    if "jpg" in original_image:
        original_image_path = os.path.join(path, original_image)
        new_image_path = os.path.join(new_path, original_image)
        image = cv2.imread(original_image_path)
        image_cropped = image[281:343, 109:171]
        cv2.imwrite(new_image_path, image_cropped)
        print(f"Imagen {original_image} cortada")

    else:
        print(f"{original_image} no es uan imagen")



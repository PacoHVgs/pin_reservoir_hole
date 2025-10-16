from realesrgan import RealESRGANer
from PIL import Image

model = RealESRGANer('cuda')  # or 'cpu'
model.load_weights('RealESRGAN_x4.pth')  # Download model

image = Image.open('image_small.jpg')
sr_image = model.predict(image)

# Resize to exactly 150x150
sr_image = sr_image.resize((150, 150), Image.LANCZOS)
sr_image.save('output_realesrgan.png')
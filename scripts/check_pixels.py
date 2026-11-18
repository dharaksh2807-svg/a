from PIL import Image
import numpy as np

img = Image.open("production_v3/prototype/renders/nyra_prototype_head_front.png")
arr = np.array(img)
face_pixels = arr[350:650, 400:624] # center of face
print("Face pixel mean:", face_pixels.mean(axis=(0,1)))
print("Face pixel max:", face_pixels.max(axis=(0,1)))
print("Face pixel min:", face_pixels.min(axis=(0,1)))

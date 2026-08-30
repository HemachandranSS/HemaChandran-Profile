import os
from PIL import Image

# Configuration
input_folder = './'
output_folder = os.path.join(input_folder, 'cropped_results')
crop_amount = 50

# Create output directory if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

for filename in os.listdir(input_folder):
    if filename.lower().endswith('.png'):
        img_path = os.path.join(input_folder, filename)
        
        with Image.open(img_path) as img:
            width, height = img.size
            
            # Define the bounding box: (left, top, right, bottom)
            # We subtract the border from the right and bottom dimensions
            left = crop_amount
            top = crop_amount
            right = width - crop_amount
            bottom = height - crop_amount
            
            # Ensure the crop is valid (for very small images)
            if right > left and bottom > top:
                cropped_img = img.crop((left, top, right, bottom))
                cropped_img.save(os.path.join(output_folder, filename))
                print(f"Processed: {filename}")
            else:
                print(f"Skipped {filename}: Image too small to crop.")

print("Done! Check the 'cropped_results' folder.")
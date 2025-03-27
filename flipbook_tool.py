import os
import sys
import math
from PIL import Image
import re

def calc_grid_size(num_frames):
    sqrt_val = int(math.sqrt(num_frames))
    for rows in range(sqrt_val, 0, -1):
        if num_frames % rows == 0:
            cols = num_frames // rows
            return (rows, cols)
    return (1, num_frames)

def sort_image_files(image_files):
    # Sort files based on numeric value in the filename
    def extract_number(filename):
        match = re.search(r'(\d+)', filename)
        return int(match.group(0)) if match else float('inf')

    return sorted(image_files, key=extract_number)

def pack_spritesheet(folder_path):
    # Get all image files in the folder
    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
    num_frames = len(image_files)

    if num_frames == 0:
        print("No images found in the specified folder.")
        return

    # Sort the image files
    image_files = sort_image_files(image_files)

    # Open the first image to get the size
    first_image = Image.open(os.path.join(folder_path, image_files[0]))
    frame_width, frame_height = first_image.size

    # Calculate grid size
    rows, cols = calc_grid_size(num_frames)

    # Create a new blank image for the spritesheet
    spritesheet_width = cols * frame_width
    spritesheet_height = rows * frame_height
    spritesheet = Image.new('RGBA', (spritesheet_width, spritesheet_height))

    # Paste each image into the spritesheet
    for index, image_file in enumerate(image_files):
        img = Image.open(os.path.join(folder_path, image_file))
        x = (index % cols) * frame_width
        y = (index // cols) * frame_height
        spritesheet.paste(img, (x, y))

    # Save the spritesheet with the specified naming convention
    output_filename = f"flipbook_{rows}x{cols}.tga"
    output_path = os.path.join(folder_path, output_filename)
    spritesheet.save(output_path)
    print(f"Spritesheet created at: {output_path}")

def unpack_spritesheet(image_path, dimensions):
    # Create a folder for the unpacked frames
    output_folder = os.path.splitext(os.path.basename(image_path))[0]
    os.makedirs(output_folder, exist_ok=True)

    # Open the spritesheet
    spritesheet = Image.open(image_path)

    # Parse dimensions
    rows, cols = map(int, dimensions.split(':'))

    # Calculate frame size
    frame_width = spritesheet.width // cols
    frame_height = spritesheet.height // rows

    # Extract frames
    for row in range(rows):
        for col in range(cols):
            left = col * frame_width
            upper = row * frame_height
            right = left + frame_width
            lower = upper + frame_height
            frame = spritesheet.crop((left, upper, right, lower))
            frame.save(os.path.join(output_folder, f"frame_{row * cols + col:04d}.png"))

    print(f"Unpacked {rows * cols} frames into folder: {output_folder}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: \n python flipbook_tool.py <folder_of_my_frames> to pack a flipbook OR\n python flipbook_tool.py <spritesheet_image> <rows:cols> to unpack a spritesheet")
        sys.exit(1)

    # Check if the first argument is a directory or a file
    first_arg = sys.argv[1]
    if os.path.isdir(first_arg):
        pack_spritesheet(first_arg)
    elif os.path.isfile(first_arg) and len(sys.argv) == 3:
        image_path = first_arg
        dimensions = sys.argv[2]
        unpack_spritesheet(image_path, dimensions)
    else:
        print("Invalid arguments. Please provide a valid directory for packing or a valid spritesheet image with dimensions for unpacking.")
        sys.exit(1)

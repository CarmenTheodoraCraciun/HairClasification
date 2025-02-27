import os
import cv2
import numpy as np
import random
import shutil

def is_image(file_path):
    try:
        img = cv2.imread(file_path)
        return img is not None
    except:
        return False

def resize_image(img, size):
    """
    Resizes an image using bilinear interpolation.

    Args:
        img: Input image.
        size: Desired size of the output image (width, height).

    Returns:
        Resized image.
    """
    original_height, original_width, _ = img.shape
    new_width, new_height = size
    resized_img = np.zeros((new_height, new_width, 3), dtype=np.uint8)

    for i in range(new_width):
        for j in range(new_height):
            #i, j = pixel in the resized image
            # x, y = pixel in the original image
            x = i * (original_width - 1) / (new_width - 1)
            y = j * (original_height - 1) / (new_height - 1)

            # Neighborhood values
            x0 = int(np.floor(x))
            x1 = min(x0 + 1, original_width - 1) 
            y0 = int(np.floor(y))
            y1 = min(y0 + 1, original_height - 1)

            # Extract the intensity values ​​of neighbors
            Ia = img[y0, x0] # stanga sus
            Ib = img[y0, x1] # drepata sus
            Ic = img[y1, x0] # stanga jos
            Id = img[y1, x1] # dreapta jos

            # Calculates the weight of each neighboring to the final value
            wa = (x1 - x) * (y1 - y)
            wb = (x - x0) * (y1 - y)
            wc = (x1 - x) * (y - y0)
            wd = (x - x0) * (y - y0)

            # The final value of the new pixel
            pixel = wa * Ia + wb * Ib + wc * Ic + wd * Id
            resized_img[j, i] = np.round(pixel).astype(int)

    return resized_img

def augment_image(img, size=(128, 128), shear_range=0.1, zoom_range=0.1, horizontal_flip=True):
    """
    Preprocesses and augments an image by applying resizing, shearing, zooming, and horizontal flipping.

    Args:
        img: Input image.
        size: Desired size of the output image (width, height).
        shear_range: Range for random shearing.
        zoom_range: Range for random zooming.
        horizontal_flip: Whether to randomly flip the image horizontally.

    Returns:
        Preprocessed and augmented image.
    """
    rows, cols, ch = img.shape
    shear_factor = np.random.uniform(-shear_range, shear_range)
    M_shear = np.array([[1, shear_factor, 0], [0, 1, 0]], dtype=np.float32)
    img = cv2.warpAffine(img, M_shear, (cols, rows))

    zoom_factor = np.random.uniform(1 - zoom_range, 1 + zoom_range)
    img = cv2.resize(img, None, fx=zoom_factor, fy=zoom_factor)

    if zoom_factor < 1: # zoom out
        new_height, new_width = img.shape[:2]
        # Number of pixels added to padding (black) and its addition
        pad_height = (rows - new_height) // 2
        pad_width = (cols - new_width) // 2
        img = cv2.copyMakeBorder(img, pad_height, pad_height,
            pad_width, pad_width, cv2.BORDER_CONSTANT, value=[0, 0, 0])
    else: # zoom in
        # Position of the starting point for cutting
        start_x = (img.shape[1] - cols) // 2
        start_y = (img.shape[0] - rows) // 2
        img = img[start_y:start_y + rows, start_x:start_x + cols]

    if horizontal_flip and np.random.random() < 0.5:
        img = cv2.flip(img, 1)

    img = cv2.resize(img, size)

    return img

def preprocess_images(input_dir, output_dir, size=(128, 128), augment_prob=0.3):
    """
    Resizes images to the specified size and saves them to the output directory.
    Applies augmentations to a random subset of images.

    Args:
        input_dir: Directory containing the input images.
        output_dir: Directory to save the preprocessed images.
        size: Desired size of the output images (width, height).
        augment_prob: Probability of applying augmentation to each image.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print("Start processing data.")
    for category in os.listdir(input_dir):
        category_dir = os.path.join(input_dir, category)
        output_category_dir = os.path.join(output_dir, category)
        if not os.path.exists(output_category_dir):
            os.makedirs(output_category_dir)

        num_images = 0
        if os.path.isdir(category_dir):
            for idx, img_name in enumerate(os.listdir(category_dir)):
                img_path = os.path.join(category_dir, img_name)

                if is_image(img_path):
                    img = cv2.imread(img_path)
                    if img is not None:
                        if np.random.rand() < augment_prob:
                            img = augment_image(img, size=size)
                        else:
                            img = resize_image(img, size)
                        new_img_name = f"{category}_{idx}.png"
                        cv2.imwrite(os.path.join(output_category_dir, new_img_name), img)
                        num_images += 1
                    else:
                        print(f"Failed to load image: {img_path}")
                else:
                    print(f"Not an image: {img_path}")
            
        print(f"Folder {output_category_dir} has {num_images} images.")
    
    print("The data are processed.")

preprocess_images('./originalData', './processData')
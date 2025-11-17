import os
import numpy as np
import cv2
import argparse
from multiprocessing import Pool
from pathlib import Path


def image_write(path_A, path_B, path_AB):
    """Combine two images side by side."""
    try:
        im_A = cv2.imread(str(path_A), cv2.IMREAD_COLOR)
        im_B = cv2.imread(str(path_B), cv2.IMREAD_COLOR)
        
        if im_A is None:
            print(f"Warning: Could not read image {path_A}")
            return False
        if im_B is None:
            print(f"Warning: Could not read image {path_B}")
            return False
        
        # Ensure both images have the same height
        h_A, w_A = im_A.shape[:2]
        h_B, w_B = im_B.shape[:2]
        
        if h_A != h_B:
            # Resize to match the smaller height
            target_h = min(h_A, h_B)
            im_A = cv2.resize(im_A, (int(w_A * target_h / h_A), target_h))
            im_B = cv2.resize(im_B, (int(w_B * target_h / h_B), target_h))
        
        im_AB = np.concatenate([im_A, im_B], 1)
        cv2.imwrite(str(path_AB), im_AB)
        return True
    except Exception as e:
        print(f"Error processing {path_A} and {path_B}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser('create image pairs')
    parser.add_argument('--fold_A', dest='fold_A', help='input directory for image A', type=str, default='../dataset/50kshoes_edges')
    parser.add_argument('--fold_B', dest='fold_B', help='input directory for image B', type=str, default='../dataset/50kshoes_jpg')
    parser.add_argument('--fold_AB', dest='fold_AB', help='output directory', type=str, default='../dataset/test_AB')
    parser.add_argument('--num_imgs', dest='num_imgs', help='number of images', type=int, default=1000000)
    parser.add_argument('--use_AB', dest='use_AB', help='if true: (0001_A, 0001_B) to (0001_AB)', action='store_true')
    parser.add_argument('--no_multiprocessing', dest='no_multiprocessing', help='If used, chooses single CPU execution instead of parallel execution', action='store_true', default=False)
    args = parser.parse_args()

    for arg in vars(args):
        print('[%s] = ' % arg, getattr(args, arg))

    fold_A = Path(args.fold_A)
    fold_B = Path(args.fold_B)
    fold_AB = Path(args.fold_AB)

    # Check if directories exist
    if not fold_A.exists():
        print(f"Error: Directory {fold_A} does not exist!")
        return
    if not fold_B.exists():
        print(f"Error: Directory {fold_B} does not exist!")
        return

    # Get subdirectories or use root if no subdirectories
    splits = [p.name for p in fold_A.iterdir() if p.is_dir()]
    
    # If no subdirectories, treat the root as a single split
    if not splits:
        splits = ['.']
        print("No subdirectories found. Processing images directly in A and B folders.")

    pool = None
    if not args.no_multiprocessing:
        pool = Pool()

    total_processed = 0
    total_errors = 0

    for sp in splits:
        if sp == '.':
            img_fold_A = fold_A
            img_fold_B = fold_B
            img_fold_AB = fold_AB
        else:
            img_fold_A = fold_A / sp
            img_fold_B = fold_B / sp
            img_fold_AB = fold_AB / sp

        if not img_fold_A.exists():
            print(f"Warning: {img_fold_A} does not exist. Skipping...")
            continue
        if not img_fold_B.exists():
            print(f"Warning: {img_fold_B} does not exist. Skipping...")
            continue

        # Get image files
        img_list = []
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']:
            img_list.extend([p.name for p in img_fold_A.glob(ext) if p.is_file()])
        
        if args.use_AB:
            img_list = [img_path for img_path in img_list if '_A.' in img_path]

        if not img_list:
            print(f"Warning: No images found in {img_fold_A}. Skipping...")
            continue

        num_imgs = min(args.num_imgs, len(img_list))
        print(f'split = {sp}, use {num_imgs}/{len(img_list)} images')
        
        img_fold_AB.mkdir(parents=True, exist_ok=True)
        print(f'split = {sp}, number of images = {num_imgs}')

        tasks = []
        for n in range(num_imgs):
            name_A = img_list[n]
            path_A = img_fold_A / name_A
            if args.use_AB:
                name_B = name_A.replace('_A.', '_B.')
            else:
                name_B = name_A
            path_B = img_fold_B / name_B
            
            if not path_A.is_file():
                print(f"Warning: {path_A} is not a file. Skipping...")
                total_errors += 1
                continue
            if not path_B.is_file():
                print(f"Warning: {path_B} is not a file. Skipping...")
                total_errors += 1
                continue

            name_AB = name_A
            if args.use_AB:
                name_AB = name_AB.replace('_A.', '.')  # remove _A
            path_AB = img_fold_AB / name_AB

            if not args.no_multiprocessing:
                tasks.append((path_A, path_B, path_AB))
            else:
                if image_write(path_A, path_B, path_AB):
                    total_processed += 1
                else:
                    total_errors += 1

        # Process tasks in parallel if multiprocessing is enabled
        if not args.no_multiprocessing and tasks:
            results = [pool.apply_async(image_write, args=task) for task in tasks]
            for result in results:
                if result.get():
                    total_processed += 1
                else:
                    total_errors += 1

    if pool:
        pool.close()
        pool.join()

    print(f"\nCompleted! Processed: {total_processed}, Errors: {total_errors}")


if __name__ == '__main__':
    main()

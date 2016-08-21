import dlib
import os
import json
from skimage import io

image_dir = "/Users/sundeepblue/movie/full"

# populate image path
files = os.listdir(image_dir)
image_paths = [os.path.join(image_dir, f) for f in files if f.endswith("jpg")]

detector = dlib.get_frontal_face_detector()

image_and_facenumber_pair_list = []
show_window = False

for i, path in enumerate(image_paths):
    if i % 10 == 0:
        print "{}/{}".format(i+1, len(image_paths))

    meta = {}

    image_id = path.split("/")[-1].split(".")[0]
    meta['image_id'] = image_id

    img = io.imread(path)
    dets = detector(img, 1) # Run the face detector, upsampling the image 1 time to find smaller faces.

    meta['num_faces'] = len(dets)
    print "{} faces were detected in image {}: ".format(len(dets), path)

    image_and_facenumber_pair_list.append(meta)

    if show_window:
        win = dlib.image_window()
        win.set_image(img)
        win.add_overlay(dets)
        raw_input("Hit enter to continue")

with open("image_and_facenumber_pair_list.json", "w") as f:
    json.dump(image_and_facenumber_pair_list, f)

print "Face detection for all images finished!"
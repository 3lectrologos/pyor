import csv
import os


def is_valid(nid, fid):
    img_name = nid + '_' + fid + '.jpg'
    return os.path.exists(os.path.join(DIR_VALID_IMAGES, img_name))

def filter_photo_list(fin, fout):
    with open(fin, 'r') as csvin, open(fout, 'w') as csvout:
        reader = csv.reader(csvin)
        writer = csv.writer(csvout)
        for row in reader:
            if is_valid(row[0], row[1]):
                writer.writerow(row)

DIR_VALID_IMAGES = 'valid_images'
FILE_ALL_IMAGES = 'all_images.csv'
FILE_VALID_IMAGES = 'valid_images.csv'

filter_photo_list(FILE_ALL_IMAGES, FILE_VALID_IMAGES)

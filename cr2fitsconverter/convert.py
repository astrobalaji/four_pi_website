import rawpy
import exifread
from astropy.io import fits
import os
from tqdm import tqdm

def convert(filename):
    data = rawpy.imread(open(filename, 'rb'))
    meta_data = exifread.process_file(open(filename, 'rb'))

    img = data.postprocess()
    img_r = img[:,:,0]
    img_g = img[:,:,1]
    img_b = img[:,:,2]

    fits_img = fits.PrimaryHDU(img_r)
    fits_img.header['Exposure'] = str(meta_data['EXIF ExposureTime'].values[0])
    fits_img.header['Date'] = str(meta_data['Image DateTime'].values)
    fits_img.header['Camera'] = str(meta_data['Image Model'].values)
    fits_img.header['Channel'] = 'Red'
    fits_img.writeto(filename.replace('.CR2', '_r.fits'))

    fits_img = fits.PrimaryHDU(img_g)
    fits_img.header['Exposure'] = str(meta_data['EXIF ExposureTime'].values[0])
    fits_img.header['Date'] = str(meta_data['Image DateTime'].values)
    fits_img.header['Camera'] = str(meta_data['Image Model'].values)
    fits_img.header['Channel'] = 'Green'
    fits_img.writeto(filename.replace('.CR2', '_g.fits'))

    fits_img = fits.PrimaryHDU(img_b)
    fits_img.header['Exposure'] = str(meta_data['EXIF ExposureTime'].values[0])
    fits_img.header['Date'] = str(meta_data['Image DateTime'].values)
    fits_img.header['Camera'] = str(meta_data['Image Model'].values)
    fits_img.header['Channel'] = 'Blue'
    fits_img.writeto(filename.replace('.CR2', '_b.fits'))

os.chdir('/Users/astrobalaji/Desktop/4pi_data/lights')
filenames = os.listdir()
for f in tqdm(filenames):
    convert(f)

print('finished lights!!!')

os.chdir('/Users/astrobalaji/Desktop/4pi_data/darks')
filenames = os.listdir()
for f in tqdm(filenames):
    convert(f)

print('finished darks!!!')

os.chdir('/Users/astrobalaji/Desktop/4pi_data/bias')
filenames = os.listdir()
for f in tqdm(filenames):
    convert(f)

print('finished bias!!!')

os.chdir('/Users/astrobalaji/Desktop/4pi_data/flats')
filenames = os.listdir()
for f in tqdm(filenames):
    convert(f)

print('finished flats')

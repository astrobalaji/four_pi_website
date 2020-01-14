import rawpy
import exifread
from astropy.io import fits
import os
from tqdm import tqdm

os.chdir('/Users/astrobalaji/Documents/four_pi_live/four_pi_website/cr2fitsconverter')

def convert(filename):
    data = rawpy.imread(open(filename, 'rb'))
    meta_data = exifread.process_file(open(filename, 'rb'))

    img = data.postprocess()
    img_r = img[:,:,0]
    img_g = img[:,:,1]
    img_b = img[:,:,2]

    fits_img = fits.PrimaryHDU(img_r)
    exposure = meta_data['EXIF ExposureTime'].values[0]
    exp_time = float(exposure.num/exposure.den)
    fits_img.header['Exposure'] = exp_time
    fits_img.header['Date'] = str(meta_data['Image DateTime'].values)
    fits_img.header['Camera'] = str(meta_data['Image Model'].values)
    fits_img.header['Channel'] = 'Red'
    fits_img.writeto(filename.replace('.CR2', '_{0}_r.fits'.format(exp_time)))

    fits_img = fits.PrimaryHDU(img_g)
    exposure = meta_data['EXIF ExposureTime'].values[0]
    exp_time = float(exposure.num/exposure.den)
    fits_img.header['Exposure'] = exp_time
    fits_img.header['Date'] = str(meta_data['Image DateTime'].values)
    fits_img.header['Camera'] = str(meta_data['Image Model'].values)
    fits_img.header['Channel'] = 'Green'
    fits_img.writeto(filename.replace('.CR2', '_{0}_g.fits'.format(exp_time)))

    fits_img = fits.PrimaryHDU(img_b)
    exposure = meta_data['EXIF ExposureTime'].values[0]
    exp_time = float(exposure.num/exposure.den)
    fits_img.header['Exposure'] = exp_time
    fits_img.header['Date'] = str(meta_data['Image DateTime'].values)
    fits_img.header['Camera'] = str(meta_data['Image Model'].values)
    fits_img.header['Channel'] = 'Blue'
    fits_img.writeto(filename.replace('.CR2', '_{0}_b.fits'.format(exp_time)))

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

import os
import re
import shutil

cwd = os.getcwd()

lights_list = os.listdir('lights/')
darks_list = os.listdir('darks/')


def exp_extract(filename):
    poslist = [p.span() for p in re.finditer('_', filename)]
    return filename[poslist[-2][1]:poslist[-1][0]]

for fname in lights_list:
    exp = exp_extract(fname)
    if not os.path.exists(cwd+'/lights/'+exp+'/'):
        os.mkdir('lights/'+exp)
    shutil.move('lights/'+fname, 'lights/'+exp+'/')

for fname in darks_list:
    exp = exp_extract(fname)
    if not os.path.exists(cwd+'/darks/'+exp+'/'):
        os.mkdir('darks/'+exp)
    shutil.move('darks/'+fname, 'darks/'+exp+'/')

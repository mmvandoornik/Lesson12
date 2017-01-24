import os
from osgeo import gdal
import numpy as np
from osgeo.gdalconst import GA_ReadOnly, GDT_Float32
import matplotlib.pyplot as plt

os.chdir("/home/ubuntu/userdata/lesson12")

# Assign files to variables
band4 = './data/LC81980242014260LGN00_sr_band4.tif'
band5 = './data/LC81980242014260LGN00_sr_band5.tif'

# Open the files
dsband4 = gdal.Open(band4, GA_ReadOnly)
dsband5 = gdal.Open(band5, GA_ReadOnly)

# Read the files as numpy array
band4Arr = dsband4.ReadAsArray(0,0,dsband4.RasterXSize, dsband4.RasterYSize)
band5Arr = dsband5.ReadAsArray(0,0,dsband5.RasterXSize, dsband5.RasterYSize)

# Set data type of the files
band4Arr = band4Arr.astype(np.float32)
band5Arr = band5Arr.astype(np.float32)

# Calculate NDWI
def ndwiCalc(NIR, MIR):
    mask = np.greater(MIR+NIR,0)
    with np.errstate(invalid='ignore'):
        ndwi = np.choose(mask,(-99,(NIR-MIR)/(NIR+MIR)))    
    return ndwi

ndwi_ = ndwiCalc(band4Arr, band5Arr)

# Write the result to disk
driver = gdal.GetDriverByName('GTiff')
outDataSet = driver.Create('./data/ndwi.tif', dsband4.RasterXSize, dsband4.RasterYSize, 1, GDT_Float32)
outBand = outDataSet.GetRasterBand(1)
outBand.WriteArray(ndwi_,0,0)
outBand.SetNoDataValue(-99)
outDataSet.SetProjection(dsband4.GetProjection())
outDataSet.SetGeoTransform(dsband4.GetGeoTransform())
outBand.FlushCache()
outDataSet.FlushCache()

# change projection to lat/lon
os.system('gdalwarp -t_srs "EPSG:4326" ./data/ndwi.tif ./data/ndwi_ll.tif')

# Plot image
#%matplotlib inline
dsll = gdal.Open("./data/ndwi_ll.tif")
ndwi = dsll.ReadAsArray(0, 0, dsll.RasterXSize, dsll.RasterYSize)
plt.imshow(ndwi, interpolation='nearest', vmin=0, cmap=plt.cm.gist_earth)
plt.show()
dsll = None
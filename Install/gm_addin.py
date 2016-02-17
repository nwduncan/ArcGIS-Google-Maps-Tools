import arcpy
import pythonaddins
import webbrowser
import pyproj
import threading
import functools

## Runs browser opening function in its own thread to
## prevent conflicts with the OS
def runThread(function):
    @functools.wraps(function)
    def fn_(*args, **kwargs):
        thread = threading.Thread(target=function, args=args, kwargs=kwargs)
        thread.start()
        thread.join()
    return fn_

## Open the browser at the selected location
def openMap():
    mxd = arcpy.mapping.MapDocument("CURRENT") # current document
    view = mxd.activeView # view
    # make sure the user is in data view
    if view == "PAGE_LAYOUT":
        pythonaddins.MessageBox("This tool will not work in Layout View. "
                              + "Please change to Data View before running",
                                "Error", 0)
    else:
        df = arcpy.mapping.ListDataFrames(mxd)[0] # data frame object
        sr = df.spatialReference # spatial reference object
        code = sr.factoryCode # epsg code
        XMin = df.extent.XMin # get min easting value
        YMin = df.extent.YMin # get min northing value
        XMax = df.extent.XMax # get max easting value
        YMax = df.extent.YMax # get max northing value
        scale = int(df.scale) # get scale
        # equivalent zoom values for Google Maps
        scaleDict = {
            1128: 19,
            2257: 18,
            4514: 17,
            9028: 16,
            18056: 15,
            36112: 14,
            72224: 13,
            144448: 12,
            288895: 11,
            577791: 10,
            1155581: 9,
            2311162: 8,
            4622325: 7,
            9244649: 6,
            18489298: 5,
            36978597: 4,
            73957194: 3,
            147914388: 2,
            295828775: 1,
            591657551: 1,
        }
        # find the equivalent (or closest to) value for current ArcMap scale
        gScale = scaleDict[min(scaleDict, key=lambda x:abs(x-scale))]
        # return centre coordinates of screen
        xy = cCCalc(XMin, YMin, XMax, YMax)
        # convert coordinates to lat/long
        inProj = pyproj.Proj(init="epsg:"+str(code)) # in projection
        outProj = pyproj.Proj(init="epsg:4326") # out projection (WGS84)
        output = pyproj.transform(inProj, outProj, xy[0], xy[1]) # output
        # address to navigate to
        gAddress = ("https://www.google.com.au/maps/@"
                + str(output[1]) + ","
                + str(output[0]) + ","
                + str(gScale) + "z"
                )
        # run browser.open function in another thread
        # to prevent it crashing ArcMap
        openGMaps = runThread(webbrowser.open)
        openGMaps(gAddress, new=0, autoraise=True)

## Calculates the centrepoint, returning the x and y as a tuple
def cCCalc(XMin, YMin, XMax, YMax):
    x = (XMax+XMin)/2
    y = (YMax+YMin)/2
    return (x, y)

def openView(xy):
    mxd = arcpy.mapping.MapDocument("CURRENT") # current document
    view = mxd.activeView # view
    if view == "PAGE_LAYOUT":
        pythonaddins.MessageBox("This tool will not work in Layout View. "
                              + "Please change to Data View before running",
                                "Error", 0)
    else:
        df = arcpy.mapping.ListDataFrames(mxd)[0] # data frame object
        sr = df.spatialReference # spatial reference object
        code = sr.factoryCode # epsg code
        # convert coordinates to lat/long
        inProj = pyproj.Proj(init="epsg:"+str(code)) # in projection
        outProj = pyproj.Proj(init="epsg:4326") # out projectiong (WGS84)
        output = pyproj.transform(inProj, outProj, xy[0], xy[1]) # output
        gAddress = ("https://www.google.com/maps?cbll="
                    + str(output[1]) + ","
                    + str(output[0]) + "&cbp=12,90,0,0,5&layer=c"
                    )
        # run browser.open function in another thread
        # to prevent it crashing ArcMap
        openGMaps = runThread(webbrowser.open)
        openGMaps(gAddress, new=0, autoraise=True)
        print gAddress

# map view button class
class MapButton1(object):
    """Implementation for GM.MapButton1 (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        openMap()

# street view button class
class SVTool1(object):
    """Implementation for GM.SVTool1 (Tool)"""
    def __init__(self):
        self.enabled = True
        self.shape = "NONE"
        self.cursor = 3
    def onMouseDownMap(self, x, y, button, shift):
        xy = (x, y)
        openView(xy)

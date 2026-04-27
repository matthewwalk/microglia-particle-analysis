#@ String input
#@ String results
#@ String outlines
#@ String binary
#@ String channel
#@ String z_project
#@ String threshold_method
#@ String threshold_min
#@ String threshold_max
#@ String size
#@ String circularity
#@ String pixel_width_um
#@ String pixel_height_um
#@ String foreground

# pyright: reportMissingImports=false, reportUndefinedVariable=false
from ij import IJ, ImagePlus
from ij.io import FileSaver
from ij.measure import Measurements, ResultsTable
from ij.plugin import ChannelSplitter, ZProjector
from ij.plugin.filter import ParticleAnalyzer
from ij.process import ByteProcessor
from loci.plugins import BF

ImporterOptions = __import__("loci.plugins.in", fromlist=["ImporterOptions"]).ImporterOptions


def parse_range(value):
    parts = value.split("-")
    if len(parts) != 2:
        raise ValueError("Expected range like 20-Infinity, got: " + value)
    lower = float(parts[0])
    upper = float("inf") if parts[1].lower() == "infinity" else float(parts[1])
    return lower, upper


def pixel_area_um2(imp):
    calibration = imp.getCalibration()
    return calibration.pixelWidth * calibration.pixelHeight


def to_pixel_area_range(imp, min_area_um2, max_area_um2):
    area_per_pixel_um2 = pixel_area_um2(imp)
    if area_per_pixel_um2 <= 0:
        raise RuntimeError("Invalid image calibration: pixel area is <= 0")
    min_area_pixels = min_area_um2 / area_per_pixel_um2
    if max_area_um2 == float("inf"):
        max_area_pixels = float("inf")
    else:
        max_area_pixels = max_area_um2 / area_per_pixel_um2
    return min_area_pixels, max_area_pixels


def project_stack(imp, method):
    if imp.getNSlices() <= 1:
        return imp

    projector = ZProjector(imp)
    if method == "max":
        projector.setMethod(ZProjector.MAX_METHOD)
    elif method == "sum":
        projector.setMethod(ZProjector.SUM_METHOD)
    else:
        projector.setMethod(ZProjector.AVG_METHOD)
    projector.doProjection()
    return projector.getProjection()


def open_channel(path, channel_index):
    options = ImporterOptions()
    options.setId(path)
    options.setAutoscale(True)
    imps = BF.openImagePlus(options)
    if len(imps) < 1:
        raise RuntimeError("Bio-Formats opened no images: " + path)

    imp = imps[0]
    channels = ChannelSplitter.split(imp)
    if len(channels) >= channel_index:
        return channels[channel_index - 1]
    return imp


def make_binary_mask(imp, threshold_low, threshold_high, foreground_value):
    processor = imp.getProcessor()
    width = processor.getWidth()
    height = processor.getHeight()
    mask = ByteProcessor(width, height)
    for y in range(height):
        for x in range(width):
            value = processor.getPixelValue(x, y)
            if threshold_low <= value <= threshold_high:
                mask.putPixel(x, y, foreground_value)
            else:
                mask.putPixel(x, y, 255 - foreground_value)
    mask_imp = ImagePlus(imp.getTitle() + "-mask", mask)
    mask_imp.setCalibration(imp.getCalibration().copy())
    return mask_imp


channel_index = int(channel) + 1
threshold_min_value = threshold_min.strip()
threshold_max_value = threshold_max.strip()
pixel_width_um_value = pixel_width_um.strip()
pixel_height_um_value = pixel_height_um.strip()
foreground_value = 0 if foreground.strip().lower() == "dark" else 255
min_size_um2, max_size_um2 = parse_range(size)
min_circularity, max_circularity = parse_range(circularity)

IJ.run("Close All")
imp = open_channel(input, channel_index)
imp = project_stack(imp, z_project)
if pixel_width_um_value and pixel_height_um_value:
    calibration = imp.getCalibration()
    calibration.pixelWidth = float(pixel_width_um_value)
    calibration.pixelHeight = float(pixel_height_um_value)
    calibration.setUnit("micron")
    imp.setCalibration(calibration)

IJ.run(imp, "8-bit", "")
if threshold_min_value and threshold_max_value:
    threshold_low = float(threshold_min_value)
    threshold_high = float(threshold_max_value)
else:
    IJ.setAutoThreshold(imp, threshold_method)
    threshold_low = imp.getProcessor().getMinThreshold()
    threshold_high = imp.getProcessor().getMaxThreshold()

imp = make_binary_mask(imp, threshold_low, threshold_high, foreground_value)
FileSaver(imp).saveAsTiff(binary)

if foreground_value == 0:
    IJ.run(imp, "Invert", "")

results_table = ResultsTable()
measurements = Measurements.AREA | Measurements.MEAN | Measurements.MIN_MAX
options = ParticleAnalyzer.SHOW_OUTLINES | ParticleAnalyzer.CLEAR_WORKSHEET
min_size_pixels, max_size_pixels = to_pixel_area_range(imp, min_size_um2, max_size_um2)
analyser = ParticleAnalyzer(
    options,
    measurements,
    results_table,
    min_size_pixels,
    max_size_pixels,
    min_circularity,
    max_circularity,
)

if not analyser.analyze(imp):
    raise RuntimeError(f"Particle analysis failed: {input}")

results_table.save(results)
outline_image = analyser.getOutputImage()
if outline_image is not None:
    FileSaver(outline_image).saveAsTiff(outlines)

IJ.run("Close All")

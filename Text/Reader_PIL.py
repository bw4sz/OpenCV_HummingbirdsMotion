try:
    import Image
except ImportError:
    from PIL import Image
import pytesseract

img = Image.open('C:/Users/Ben/Dropbox/Thesis/Maquipucuna_SantaLucia/HolgerCameras/201608/43.jpg')
img.load()
i = pytesseract.image_to_string(img)
print i
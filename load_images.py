from PIL import Image


def openFileAsByteArray():
    img = Image.open('playlists/p0/img0.jpg')
    img.load()
    img.thumbnail((64, 32))
    #img.thumbnail((10, 10))
    img = img.convert('RGB')

    width, height = img.size
    rows = []
    for i in range(height):
        rows.append([])
        for j in range(width):
            r, g, b = img.getpixel((i, j))
            rows[i].extend([bytes([b]), bytes([g]), bytes([r])])
    return rows

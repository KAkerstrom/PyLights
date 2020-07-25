from PIL import Image


def openFileAsByteArray():
    img = Image.open('playlists/p0/img0.png')
    img.load()
    #img.thumbnail((64, 32))
    #img.thumbnail((10, 10))
    img = img.convert('RGB')

    width, height = img.size
    rows = []
    print(width, height)
    for i in range(height - 1):
        rows.append([])
        print('i', i)
        for j in range(width - 1):
            print('j', j)
            r, g, b = img.getpixel((i, j))
            rows[i].extend([bytes([b]), bytes([g]), bytes([r])])
    return rows

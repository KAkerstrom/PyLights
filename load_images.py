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
    for i in range(height):
        rows.append([])
        print('i', i)
        for j in range(width):
            print('j', j)
            r, g, b = img.getpixel((j, i))
            rows[i].extend([bytes([b]), bytes([g]), bytes([r])])
    return rows

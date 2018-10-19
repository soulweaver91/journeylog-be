from PIL import ExifTags


def exif_rotate(image):
    for orientation_key in ExifTags.TAGS.keys():
        if ExifTags.TAGS[orientation_key] == 'Orientation':
            break
    else:
        return image

    # noinspection PyProtectedMember
    exif = image._getexif()
    if exif is None:
        return image

    exif = dict(exif.items())

    try:
        orientation = exif[orientation_key]

        if orientation == 3:
            image = image.rotate(180, expand=True)
        elif orientation == 6:
            image = image.rotate(270, expand=True)
        elif orientation == 8:
            image = image.rotate(90, expand=True)

        return image
    except KeyError:
        return image

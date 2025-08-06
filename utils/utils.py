from os import path


def get_slug(filename):
    # Extract the slug from the filename

    return path.splitext(path.basename(filename))[0]

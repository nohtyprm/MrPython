
MRPYTHON_VERSION_MAJOR = 3
MRPYTHON_VERSION_MINOR = 99
MRPYTHON_VERSION_PATCH = 2
MRPYTHON_VERSION_TAG = "alpha"


def version_string():
    return "{}.{}.{}{}".format(MRPYTHON_VERSION_MAJOR,
                               MRPYTHON_VERSION_MINOR,
                               MRPYTHON_VERSION_PATCH,
                               "" if MRPYTHON_VERSION_TAG == "" else ("-" + MRPYTHON_VERSION_TAG))


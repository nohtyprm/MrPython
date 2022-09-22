MRPYTHON_VERSION_MAJOR = 5
MRPYTHON_VERSION_MINOR = 1
MRPYTHON_VERSION_PATCH = 0
MRPYTHON_VERSION_TAG = "alpha"


def version_string():
    return "{}.{}.{}{}".format(MRPYTHON_VERSION_MAJOR,
                               MRPYTHON_VERSION_MINOR,
                               MRPYTHON_VERSION_PATCH,
                               "" if MRPYTHON_VERSION_TAG == "" else ("-" + MRPYTHON_VERSION_TAG))

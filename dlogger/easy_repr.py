def easy_repr(obj, exclude=set()):
    class_name = type(obj).__name__
    items = [
        "%s=%r" % (k, v)
        for k, v in obj.__dict__.iteritems()
        if not k.startswith("_") and k not in exclude
    ]
    return "%s(%s)" % (class_name, ", ".join(items))

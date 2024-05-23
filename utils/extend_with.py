def extend_with(*extensions):
    def decorator(cls):
        for ext in extensions:
            for attr_name, attr_value in ext.__dict__.items():
                if not attr_name.startswith("__"):
                    setattr(cls, attr_name, attr_value)
        return cls

    return decorator

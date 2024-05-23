from typing import Optional, Callable


def hotwire_html_template_element(update_always=False, for_full_render_only=False):
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            return result

        wrapper.this_is_hotwire_func = True
        wrapper.func_name = func.__name__
        wrapper.update_always = update_always
        wrapper.for_full_render_only = for_full_render_only
        return wrapper

    return decorator


def hotwire_event_handler(trigger_id: str, check_trigger_func: Optional[Callable] = None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            return result

        wrapper.this_is_event_handler = True
        wrapper.trigger_id = trigger_id
        wrapper.check_trigger_func = check_trigger_func
        return wrapper

    return decorator

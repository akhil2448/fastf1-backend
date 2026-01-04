import math

def sanitize_for_json(obj):
    """
    Recursively convert NaN / Inf values to None
    so FastAPI can serialize safely.
    """
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}

    if isinstance(obj, list):
        return [sanitize_for_json(v) for v in obj]

    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None

    return obj
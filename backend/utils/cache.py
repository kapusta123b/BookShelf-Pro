from hashlib import md5

from dataclasses import Field
from typing import Protocol, Any, Dict

class AnyDataclass(Protocol):
    __dataclass_fields__: Dict[str, Field[Any]]

def get_cache_key(prefix: str, filters: AnyDataclass) -> str:
    filters_str = "_".join(f"{k}={v}" for k, v in sorted(filters.__dict__.items()))

    filters_hash = md5(filters_str.encode("utf-8")).hexdigest()
    
    return f"{prefix}_{filters_hash}"
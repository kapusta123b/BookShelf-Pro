from hashlib import md5

from dataclasses import Field, asdict, is_dataclass
import logging
from typing import Protocol, Any, Dict


class AnyDataclass(Protocol):
    __dataclass_fields__: Dict[str, Field[Any]]


def get_cache_key(prefix: str, filters: AnyDataclass) -> str | None:
    if not is_dataclass(filters):
        logging.critical(
            "Cache key generation failed: Provided object is not a dataclass"
        )
        return None

    if not prefix:
        logging.critical("Cache key generation failed: has no prefix")
        return None

    try:
        filters_dict = asdict(filters)

        if not filters_dict:
            raise ValueError("Dataclass is empty")

        filters_str = "_".join(f"{k}={v}" for k, v in sorted(filters_dict.items()))
        filters_hash = md5(filters_str.encode("utf-8")).hexdigest()

        return f"{prefix}_{filters_hash}"

    except ValueError as e:
        logging.warning(f"Cache key logic error: {e}")
        return None

    except Exception as e:
        logging.critical(f"Cache key generation crashed: {e}", exc_info=True)
        return None

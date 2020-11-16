from typing import *
import json
import os
import sys


default_settings = {}
settings = {}  # Exposed for diect use
_default_settings_path: Optional[str] = None
_settings_path: Optional[str] = None


def try_load(path: str, fail_creates: bool = False) -> Optional[dict]:
    d = None
    failed = False

    if os.path.exists(path) and os.path.isfile(path):
        try:
            d = json.load(open(path))
        except:
            failed |= True
    else:
        failed |= True

    if failed and fail_creates:
        try:
            json.dump({}, open(path, 'w'))
            d = {}
        except:
            pass

    return d


def load(*, path: str = ..., default_path: str = ...):
    global default_settings, settings, _default_settings_path, _settings_path

    if default_path not in (None, ...):
        d = try_load(default_path)
        if d is not None:
            default_settings = d
            _default_settings_path = default_path
    else:
        default_settings = try_load(_default_settings_path)

    if path not in (None, ...):
        d = try_load(path, True)
        if d is not None:
            settings = d
            _settings_path = path
    else:
        settings = try_load(_settings_path)

    if None in (path, default_path):
        raise RuntimeError('Settings files missing!')


def save(*, path: str = ...):
    global settings, _settings_path

    if path not in (None, ...):
        _settings_path = path

    json.dump(settings, _settings_path)


default_try_get_delim = ''

def try_get(d: Union[list, dict], k: str, delim: str = ..., fallback: Any = None):
    if delim in (None, Ellipsis):
        delim = default_try_get_delim
    k = k.split(delim) if delim else [k]
    for s in k:
        try:
            if isinstance(d, dict) and s in d:
                d = d[s]
            elif isinstance(d, list) and int(s) in d:
                d = d[int(s)]
            else:
                return fallback
        except:
            return fallback
    return d


warn_given = set()
def get(key: str, delim: str = ..., fallback: Any = None):
    val = try_get(settings, key, delim=delim)
    if val is None:
        val = try_get(default_settings, key, delim=delim)
    if val is None:
        if key not in warn_given:
            print(f"WARN settings key {key} not found! fallback to {fallback}", file=sys.stderr)
            warn_given.add(key)
        val = fallback
    return val

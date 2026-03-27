import random
import string
import base64

_PREFIXES = [
    "service", "config", "update", "handler", "manager", "buffer",
    "stream", "cache", "session", "context", "provider", "factory",
    "adapter", "worker", "process", "runtime", "system", "kernel",
    "driver", "module", "resource", "thread", "task", "event",
    "security", "network", "storage", "registry", "monitor", "loader",
    "dispatcher", "resolver", "validator", "formatter", "converter",
    "allocator", "scheduler", "controller", "wrapper", "helper",
    "init", "temp", "local", "global", "internal", "private",
]

_SUFFIXES = [
    "Data", "Info", "Result", "Value", "State", "Block", "Bytes",
    "Array", "List", "Count", "Size", "Offset", "Index", "Ptr",
    "Handle", "Token", "Key", "Ref", "Obj", "Ctx", "Buf",
    "Mgr", "Svc", "Cfg", "Tmp", "Len", "Addr", "Base",
]

_STYLES = ["camel", "pascal", "underscore", "short"]


def rand_str(length=8):
    return ''.join(random.choices(string.ascii_lowercase, k=length))


def rand_var():
    style = random.choice(_STYLES)
    if style == "camel":
        prefix = random.choice(_PREFIXES)
        suffix = random.choice(_SUFFIXES)
        return f"${prefix}{suffix}"
    elif style == "pascal":
        prefix = random.choice(_PREFIXES).capitalize()
        suffix = random.choice(_SUFFIXES)
        return f"${prefix}{suffix}"
    elif style == "underscore":
        prefix = random.choice(_PREFIXES)
        suffix = random.choice(_SUFFIXES).lower()
        return f"${prefix}_{suffix}"
    else:
        length = random.randint(3, 6)
        chars = random.choices(string.ascii_letters + string.digits, k=length)
        chars[0] = random.choice(string.ascii_letters)
        return "$" + "".join(chars)


def rand_class_name():
    parts = [random.choice(_PREFIXES).capitalize(), random.choice(_SUFFIXES)]
    return "".join(parts)


def to_b64(data: bytes) -> str:
    return base64.b64encode(data).decode('ascii')

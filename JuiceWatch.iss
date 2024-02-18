

#define MyAppName "JuiceWatch"
#define MyAppVersion "3.0"
#define MyAppPublisher "Trakexcel Studio, Inc."
#define MyAppURL "https://vickkie.github.io"
#define MyAppExeName "JuiceWatch.exe"
#define MyAppAssocName "JuiceWatch 3.0"
#define MyAppAssocExt ".exe"
#define MyAppAssocKey StringChange(MyAppAssocName, " ", "") + MyAppAssocExt

[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{200FA566-AE13-4D24-AA08-F533CC609CFA}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
;DefaultDirName=C:\Program Files\{#MyAppName}
ChangesAssociations=yes
DisableProgramGroupPage=yes
LicenseFile=C:\xampp\htdocs\trakexcel\Uzi-Battery-monitor\license.txt
InfoBeforeFile=C:\xampp\htdocs\trakexcel\Uzi-Battery-monitor\InfoBefore.txt
InfoAfterFile=C:\xampp\htdocs\trakexcel\Uzi-Battery-monitor\InfoAfter.txt
; Remove the following line to run in administrative install mode (install for all users.)
PrivilegesRequired=lowest
OutputDir=C:\Users\Quinzel\Music\Apps
OutputBaseFilename={#MyAppAssocName}
SetupIconFile=C:\xampp\htdocs\trakexcel\Uzi-Battery-monitor\icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "C:\xampp\htdocs\trakexcel\Uzi-Battery-monitor\JuiceWatch.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\xampp\htdocs\trakexcel\Uzi-Battery-monitor\icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\xampp\htdocs\trakexcel\Uzi-Battery-monitor\notify.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\xampp\htdocs\trakexcel\Uzi-Battery-monitor\icon.png"; DestDir: "{app}"; Flags: ignoreversion

; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Registry]
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocExt}\OpenWithProgids"; ValueType: string; ValueName: "{#MyAppAssocKey}"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}"; ValueType: string; ValueName: ""; ValueData: "{#MyAppAssocName}"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""
Root: HKA; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".myp"; ValueData: ""

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

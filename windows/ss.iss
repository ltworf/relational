[Setup]
AppId={{6F127615-6AD4-4BD7-8135-2444A335B5CD}
AppName=Relational
AppVerName=Relational ver. 3.0
AppPublisher=Salvo 'LtWorf' Tomaselli
AppPublisherURL=https://ltworf.github.io/relational/
AppSupportURL=https://ltworf.github.io/relational/
AppUpdatesURL=https://ltworf.github.io/relational/
DefaultDirName={pf}\Relational
DefaultGroupName=Relational
AllowNoIcons=yes
LicenseFile=COPYING
OutputBaseFilename=SetupRelational
SetupIconFile=windows\favicon.ico
Compression=lzma
SolidCompression=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Run]
; add the Parameters, WorkingDir and StatusMsg as you wish, just keep here
; the conditional installation Check
Filename: "{tmp}\python-3.8.5-amd64.exe"; Parameters: "/passive InstallAllUsers=1";
Filename: "{tmp}\pipscript.bat"

[Files]
; NOTE: Don't use "Flags: ignoreversion" on any shared system files
Source: "windows\python-3.8.5-amd64.exe"; DestDir: {tmp}; Flags: deleteafterinstall
Source: "windows\pipscript.bat"; DestDir: {tmp}; Flags: deleteafterinstall

Source: "relational.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "relational\*"; DestDir: "{app}\relational"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "relational_gui\*"; DestDir: "{app}\relational_gui"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "samples\*"; DestDir: "{app}\samples"; Flags: ignoreversion recursesubdirs createallsubdirs


[Icons]
Name: "{group}\Relational"; Filename: "{win}\pyw.exe"; Parameters: "relational.py"; WorkingDir: "{app}"
Name: "{group}\{cm:ProgramOnTheWeb,Relational}"; Filename: "https://ltworf.github.io/relational/"
Name: "{group}\{cm:UninstallProgram,Relational}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\Relational"; Tasks: desktopicon; Filename: "{win}\pyw.exe"; Parameters: "relational.py"; WorkingDir: "{app}"

[Run]
Description: "{cm:LaunchProgram,Relational}"; Flags: nowait postinstall skipifsilent; Filename: "{win}\pyw.exe"; Parameters: "relational.py"; WorkingDir: "{app}"

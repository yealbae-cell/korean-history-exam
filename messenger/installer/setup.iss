; Inno Setup Script for LAN Messenger
; Download Inno Setup: https://jrsoftware.org/isdl.php

[Setup]
AppName=LAN 메신저
AppVersion=1.0.0
AppPublisher=LAN Messenger
AppPublisherURL=https://github.com/yealbae-cell/korean-history-exam
DefaultDirName={autopf}\LAN Messenger
DefaultGroupName=LAN 메신저
OutputDir=..\dist\installer
OutputBaseFilename=LAN_Messenger_Setup_v1.0.0
SetupIconFile=app_icon.ico
UninstallDisplayIcon={app}\LAN_Messenger.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "korean"; MessagesFile: "compiler:Default.isl"

[CustomMessages]
korean.LaunchProgram=LAN 메신저 실행

[Tasks]
Name: "desktopicon"; Description: "바탕화면에 바로가기 생성"; GroupDescription: "바로가기:"; Flags: unchecked
Name: "startupicon"; Description: "Windows 시작 시 자동 실행"; GroupDescription: "자동 실행:"; Flags: unchecked

[Files]
; Main client executable
Source: "..\dist\LAN_Messenger.exe"; DestDir: "{app}"; Flags: ignoreversion
; Server executable
Source: "..\dist\LAN_Messenger_Server.exe"; DestDir: "{app}"; Flags: ignoreversion
; Icon
Source: "app_icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Start menu
Name: "{group}\LAN 메신저"; Filename: "{app}\LAN_Messenger.exe"; IconFilename: "{app}\app_icon.ico"
Name: "{group}\LAN 메신저 서버"; Filename: "{app}\LAN_Messenger_Server.exe"; IconFilename: "{app}\app_icon.ico"
Name: "{group}\LAN 메신저 제거"; Filename: "{uninstallexe}"
; Desktop
Name: "{autodesktop}\LAN 메신저"; Filename: "{app}\LAN_Messenger.exe"; IconFilename: "{app}\app_icon.ico"; Tasks: desktopicon
; Startup
Name: "{userstartup}\LAN 메신저"; Filename: "{app}\LAN_Messenger.exe"; Tasks: startupicon

[Run]
Filename: "{app}\LAN_Messenger.exe"; Description: "{cm:LaunchProgram}"; Flags: nowait postinstall skipifsilent

[Code]
// Add Windows Firewall exception during install
procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    // Add firewall rule for client
    Exec('netsh', 'advfirewall firewall add rule name="LAN Messenger" dir=in action=allow program="' + ExpandConstant('{app}\LAN_Messenger.exe') + '" enable=yes profile=private', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    // Add firewall rule for server
    Exec('netsh', 'advfirewall firewall add rule name="LAN Messenger Server" dir=in action=allow program="' + ExpandConstant('{app}\LAN_Messenger_Server.exe') + '" enable=yes profile=private', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  end;
end;

// Remove firewall rules on uninstall
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  ResultCode: Integer;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    Exec('netsh', 'advfirewall firewall delete rule name="LAN Messenger"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    Exec('netsh', 'advfirewall firewall delete rule name="LAN Messenger Server"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  end;
end;

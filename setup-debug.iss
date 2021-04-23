; Setup script for the creating a DEBUG version of Spine Toolbox.
; This script is meant for creating an application that opens a console
; when launching the app. The console MUST BE ENABLED in cx_Freeze_setup.py
; BEFORE running this script.

; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "Spine Toolbox Console"
#define MyAppVersion "0.6.0-beta.0"
#define MyAppPublisher "Spine Project Consortium"
#define MyAppURL "https://github.com/Spine-project"
#define MyAppExeName "spinetoolbox.exe"
#define MyAppRegKey "Software\SpineProject"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; AppId for the CONSOLE version
AppId={{CDB23453-4C19-4BAD-8A7F-19B68741E0F2}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={pf}\Spine Toolbox Console
DefaultGroupName=Spine Toolbox Console
AllowNoIcons=yes
LicenseFile=COPYING.LESSER
OutputBaseFilename=spine-toolbox-console-{#MyAppVersion}-x64
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin
OutputDir=dist
ArchitecturesInstallIn64BitMode=x64 ia64
ArchitecturesAllowed=x64 ia64 arm64
UsePreviousAppDir=yes

[Code]
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
  begin
    if RegKeyExists(HKEY_CURRENT_USER, '{#MyAppRegKey}') then
      if MsgBox('Do you want to delete Spine Toolbox settings from registry?',
        mbConfirmation, MB_YESNO) = IDYES
      then
        RegDeleteKeyIncludingSubkeys(HKEY_CURRENT_USER, '{#MyAppRegKey}');
  end;
end;

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "build\exe.win-amd64-3.7\spinetoolbox.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "build\exe.win-amd64-3.7\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Dirs]
Name: "{app}\projects"; Permissions: users-full
Name: "{app}\work"; Permissions: users-full

[Icons]
Name: "{group}\{#MyAppName} {#MyAppVersion}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\{#MyAppName} {#MyAppVersion}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[InstallDelete]
Type: filesandordirs; Name: "{app}\lib\numpy"
Type: filesandordirs; Name: "{app}\lib\spinedb_api\alembic"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent


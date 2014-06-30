; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!
     
[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{5C784574-7162-4518-849C-B2C13F88B122}
AppName=MotionMeerkat
AppVersion=1.4
AppPublisher=Ben Weinstein                                   
AppPublisherURL=benweinstein.weebly.com
AppSupportURL=benweinstein.weebly.com
AppUpdatesURL=benweinstein.weebly.com
DefaultDirName={pf}\MotionMeerkat
DefaultGroupName=MotionMeerkat
LicenseFile=C:\Users\Jorge\Documents\OpenCV_HummingbirdsMotion\dist\License.txt
OutputBaseFilename=MotionMeerkatSetup
Compression=lzma
SolidCompression=yes
                 
[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "C:\Users\Jorge\Documents\OpenCV_HummingbirdsMotion\dist\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs
Source: "C:\FFmpeg\bin\ffmpeg.exe";DestDir: "{app}\FFmpeg"; Flags: ignoreversion

; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\MotionMeerkat"; Filename: "{app}\motion_dev.exe"; IconFileName: "{app}\data\thumbnail.ico"
Name: "{commondesktop}\MotionMeerkat"; IconFileName: "{app}\data\thumbnail.ico"; Filename: "{app}\motion_dev.exe"; Tasks: desktopicon

[Registry]
Root: HKLM; Subkey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; ValueType: expandsz; ValueName: "Path"; ValueData: "{olddata};{app}\FFmpeg";

[Run]
Filename: "{app}\motion_dev.exe"; Description: "{cm:LaunchProgram,MotionMeerkat}"; Flags: nowait postinstall skipifsilent
Filename: "https://github.com/bw4sz/OpenCV_HummingbirdsMotion/wiki"; Flags: shellexec runasoriginaluser postinstall; Description: "Open the Wiki."
             
[Code]
function NeedsAddPath(Param: string): boolean;
var
  OrigPath: string;
begin
  if not RegQueryStringValue(HKEY_LOCAL_MACHINE,'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 'Path', OrigPath)
  then begin
    Result := True;
    exit;
  end;
  // look for the path with leading and trailing semicolon
  // Pos() returns 0 if not found
  Result := Pos(';' + UpperCase(Param) + ';', ';' + UpperCase(OrigPath) + ';') = 0;  
  if Result = True then
     Result := Pos(';' + UpperCase(Param) + '\;', ';' + UpperCase(OrigPath) + ';') = 0; 
end;

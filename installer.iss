; Inno Setup script for YouTube Downloader
; Builds an installer from the PyInstaller onedir output (dist\YouTubeDownloader)

#define MyAppName "YouTube Downloader"
#define MyAppVersion "0.7.5"
#define MyAppPublisher "CarlosArraiza"
#define MyAppExeName "YouTubeDownloader-v0.7.5.exe"
#define MySourceDir "dist\YouTubeDownloader"

[Setup]
AppId={{8F1B7C2E-2D4A-4B6E-9C3F-YOUTUBEDL001}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=installer_output
OutputBaseFilename=YouTubeDownloader-Setup-v{#MyAppVersion}
SetupIconFile=assets\icon.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequiredOverridesAllowed=commandline dialog
PrivilegesRequired=admin
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "{#MySourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

[Code]
var
  DataCheckBox: TNewCheckBox;
  DeleteUserData: Boolean;

function GetAppDataDir(): String;
begin
  Result := ExpandConstant('{localappdata}\YouTubeDownloader');
end;

function InitializeUninstall(): Boolean;
var
  Form: TSetupForm;
  OKButton, CancelButton: TNewButton;
  Lbl: TNewStaticText;
begin
  DeleteUserData := False;

  if not DirExists(GetAppDataDir()) then
  begin
    Result := True;
    Exit;
  end;

  Form := TSetupForm.Create(nil);
  try
    Form.ClientWidth := ScaleX(440);
    Form.ClientHeight := ScaleY(160);
    Form.Caption := 'Desinstalar ' + '{#MyAppName}';
    Form.Position := poScreenCenter;
    Form.BorderStyle := bsDialog;

    Lbl := TNewStaticText.Create(Form);
    Lbl.Parent := Form;
    Lbl.Left := ScaleX(16);
    Lbl.Top := ScaleY(16);
    Lbl.Width := Form.ClientWidth - ScaleX(32);
    Lbl.AutoSize := False;
    Lbl.WordWrap := True;
    Lbl.Height := ScaleY(48);
    Lbl.Caption := 'Se va a desinstalar ' + '{#MyAppName}' + '. Marca la siguiente casilla si tambien quieres eliminar tu configuracion e historial de descargas guardados.';

    DataCheckBox := TNewCheckBox.Create(Form);
    DataCheckBox.Parent := Form;
    DataCheckBox.Left := ScaleX(16);
    DataCheckBox.Top := Lbl.Top + Lbl.Height + ScaleY(12);
    DataCheckBox.Width := Form.ClientWidth - ScaleX(32);
    DataCheckBox.Height := ScaleY(34);
    DataCheckBox.Caption := 'Eliminar tambien configuracion e historial (' + GetAppDataDir() + ')';
    DataCheckBox.Checked := False;

    OKButton := TNewButton.Create(Form);
    OKButton.Parent := Form;
    OKButton.Width := ScaleX(75);
    OKButton.Height := ScaleY(23);
    OKButton.Left := Form.ClientWidth - ScaleX(16) - OKButton.Width - ScaleX(8) - OKButton.Width;
    OKButton.Top := Form.ClientHeight - ScaleY(16) - OKButton.Height;
    OKButton.Caption := 'Continuar';
    OKButton.ModalResult := mrOK;
    OKButton.Default := True;

    CancelButton := TNewButton.Create(Form);
    CancelButton.Parent := Form;
    CancelButton.Width := ScaleX(75);
    CancelButton.Height := ScaleY(23);
    CancelButton.Left := Form.ClientWidth - ScaleX(16) - CancelButton.Width;
    CancelButton.Top := Form.ClientHeight - ScaleY(16) - CancelButton.Height;
    CancelButton.Caption := 'Cancelar';
    CancelButton.ModalResult := mrCancel;
    CancelButton.Cancel := True;

    if Form.ShowModal() = mrOK then
    begin
      DeleteUserData := DataCheckBox.Checked;
      Result := True;
    end
    else
      Result := False;
  finally
    Form.Free();
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
  begin
    if DeleteUserData then
      DelTree(GetAppDataDir(), True, True, True);
  end;
end;

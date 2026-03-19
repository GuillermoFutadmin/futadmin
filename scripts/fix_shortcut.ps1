$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut("C:\Users\Memo\Desktop\FutAdmin.lnk")
$shortcut.TargetPath = "C:\Users\Memo\Desktop\FutAdmin.bat"
$shortcut.WorkingDirectory = "C:\futadmin"
$shortcut.IconLocation = "cmd.exe,0"
$shortcut.Save()
Write-Host "Shortcut updated successfully."

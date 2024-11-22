$pythonPath = "C:\Users\Administrator\AppData\Local\Programs\Python\Python310\python.exe"
$scriptPath = "C:\NodeProp\meta_handler.py"

$process = Get-Process -Name "python" 
if ($process) {
} else {
   # اجرای مجدد اسکریپت
    Start-Process -FilePath $pythonPath -ArgumentList $scriptPath
    Write-Host "Script restarted successfully."
}


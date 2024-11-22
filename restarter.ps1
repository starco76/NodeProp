# نام اسکریپت
$scriptName = "meta_handler.py"
# مسیر فایل پایتون
$pythonPath = "python.exe"
# مسیر کامل اسکریپت
$scriptPath = "C:\bot\meta_handler.py"

# یافتن و متوقف کردن فرآیند مرتبط با اسکریپت
$process = Get-Process -Name "python" 
if ($process) {
    Stop-Process -Id $process.Id -Force
    Write-Host "Process stopped successfully."
} else {
    Write-Host "No running process found for $scriptName."
}

# اجرای مجدد اسکریپت
Start-Process -FilePath $pythonPath -ArgumentList $scriptPath
Write-Host "Script restarted successfully."

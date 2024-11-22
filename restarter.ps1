# نام اسکریپت
$scriptName = "meta_handler.py"
# مسیر فایل پایتون
$pythonPath = "python.exe"
# مسیر کامل اسکریپت
$scriptPath = "C:\NodeProp\meta_handler.py"

# یافتن و متوقف کردن فرآیند مرتبط با اسکریپت
$process = Get-Process -Name "python" 
if ($process) {

} else {
   # اجرای مجدد اسکریپت
    Start-Process -FilePath $pythonPath -ArgumentList $scriptPath
    Write-Host "Script restarted successfully."
}


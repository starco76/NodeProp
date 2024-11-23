$pythonPath = "C:\python\python.exe"
$scriptPath = "C:\NodeProp\meta_handler.py"
$logFilePath = "C:\NodeProp\script_log.txt"  # مسیر فایل لاگ

# تابع برای ثبت اطلاعات در فایل لاگ
function Log-Message {
    param([string]$message)
    $timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")  # زمان ثبت
    $logMessage = "$timestamp - $message"
    $logMessage | Out-File -FilePath $logFilePath -Append  # اضافه کردن به فایل لاگ
}

# بررسی فرآیند Python در حال اجرا
$process = Get-Process -Name "python" -ErrorAction SilentlyContinue

# بررسی اینکه اسکریپت در حال اجرا است یا خیر
if ($process) {
    Log-Message "Script is already running."
} else {
    # اجرای اسکریپت پایتون
    Start-Process -FilePath $pythonPath -ArgumentList $scriptPath
    Log-Message "Script restarted successfully."
}

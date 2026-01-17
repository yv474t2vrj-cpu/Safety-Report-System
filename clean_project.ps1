# تنظيف ملفات المشروع قبل رفع إلى GitHub

Write-Host "=== تنظيف ملفات مشروع Safety Report ===" -ForegroundColor Cyan

# الملفات التي يجب حذفها
$filesToDelete = @(
    "app.py.backup",
    "app_backup.py",
    "app_backup2.py",
    "app_backup_20260114_130435.py",
    "app_cleaned.py",
    "ngrok.exe"
)

Write-Host "الملفات المراد حذفها:" -ForegroundColor Yellow
$filesToDelete | ForEach-Object { 
    if (Test-Path $_) {
        $size = (Get-Item $_).Length / 1MB
        Write-Host "  $_ (حجم: {0:N2} MB)" -f $size
    }
}

# طلب تأكيد
$confirm = Read-Host "هل تريد حذف هذه الملفات؟ (y/n)"
if ($confirm -eq 'y') {
    foreach ($file in $filesToDelete) {
        if (Test-Path $file) {
            Remove-Item $file -Force
            Write-Host "تم حذف: $file" -ForegroundColor Green
        }
    }
    Write-Host "تم الانتهاء من التنظيف!" -ForegroundColor Green
} else {
    Write-Host "تم إلغاء العملية" -ForegroundColor Red
}

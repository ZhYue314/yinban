$OutputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

function Show-Menu {
    Clear-Host
    Write-Host @"
  ╔═══════════════════════════╗
  ║      音 伴 — 选 单        ║
  ╚═══════════════════════════╝

  1. 和 AI 聊天
  2. 每日推荐
  3. 按心情推荐
  4. 按场景推荐
  5. 发现新歌手
  6. 语音播客
  7. 听歌报告
  8. 查看配置
  9. Web 界面（需安装 gradio）
  0. 退出

"@ -ForegroundColor Cyan
}

do {
    Show-Menu
    $choice = Read-Host "请选择 (0-9)"

    switch ($choice) {
        "1" { python main.py chat; pause }
        "2" { python main.py daily; pause }
        "3" {
            $mood = Read-Host "输入心情 (开心/平静/伤感/烦躁/慵懒/热情)"
            python main.py recommend --mood $mood
            pause
        }
        "4" {
            $scene = Read-Host "输入场景 (深夜/学习/跑步/通勤/工作)"
            python main.py recommend --scene $scene
            pause
        }
        "5" { python main.py discover; pause }
        "6" { python main.py podcast --no-tts; pause }
        "7" { python main.py report; pause }
        "8" { python main.py config list; pause }
        "9" { python main.py web; pause }
        "0" { break }
        default {
            Write-Host "无效输入，请重新选择" -ForegroundColor Red
            Start-Sleep -Seconds 1
        }
    }
} while ($choice -ne "0")

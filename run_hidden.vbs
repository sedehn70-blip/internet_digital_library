Set WshShell = CreateObject("WScript.Shell")
' Start Flask server
WshShell.Run "cmd /c python d:\digital_library\app.py", 0, False
' Wait for server to start (5 seconds)
WScript.Sleep 5000
' Open default browser to localhost:5000
WshShell.Run "http://localhost:5000", 1, False
Set WshShell = Nothing

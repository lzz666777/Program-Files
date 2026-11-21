$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$streamlit = "C:\电脑应用\Python\.venv\Scripts\streamlit.exe"

if (Test-Path $streamlit) {
    & $streamlit run (Join-Path $here "PG_test.py")
} else {
    streamlit run (Join-Path $here "PG_test.py")
}

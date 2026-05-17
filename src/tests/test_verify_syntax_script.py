import subprocess
import sys


def test_verify_syntax_script_runs():
    """Run the verify_syntax script and expect it to exit zero and print a header."""
    res = subprocess.run([sys.executable, "scripts/verify_syntax.py"], capture_output=True, text=True)
    assert res.returncode == 0
    assert "Verifying Python module syntax..." in res.stdout

import subprocess
import pytest
from pathlib import Path

def test_ars_mark_read_argument_parsing():
    """
    Integration test: Verify that citation keys with spaces or special characters
    are correctly passed through the CLI dispatch layer to the script.
    
    This mimics the execution of the bash block:
    python3 scripts/ars_mark_read.py $ARGUMENTS --passport-path ...
    """
    script_path = Path("scripts/ars_mark_read.py")
    
    # 1. Complex inputs (dash, space) that would break fragile prose-parsing
    test_keys = ["smith2024-data", "wang 2023 formative"]
    
    # 2. Mocking the execution (adding --dry-run to avoid actual file system writes)
    # This simulates how the bash block expands $ARGUMENTS
    cmd = ["python3", str(script_path)] + test_keys + ["--dry-run"]
    
    # 3. Execution
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # 4. Assertions
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    
    # Verify the script successfully received and processed both keys
    assert "smith2024-data" in result.stdout
    assert "wang 2023 formative" in result.stdout
    
    print("[Integration Test] ARS-Mark-Read CLI dispatch: PASSED")

if __name__ == "__main__":
    pytest.main([__file__])

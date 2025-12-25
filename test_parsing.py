import shlex
import platform
import subprocess

print(f"Platform: {platform.system()}")
posix = platform.system() != "Windows"
print(f"Using posix={posix}")

test_commands = [
    'python -c "print(\'test\')"',
    'python --version',
    'echo "hello world"',
]

for cmd in test_commands:
    print(f"\nCommand: {cmd}")
    parsed = shlex.split(cmd, posix=posix)
    print(f"Parsed: {parsed}")

    # Try to execute
    try:
        result = subprocess.run(
            parsed,
            capture_output=True,
            text=True,
            timeout=5,
            shell=False
        )
        print(f"Exit code: {result.returncode}")
        print(f"Stdout: {repr(result.stdout)}")
        print(f"Stderr: {repr(result.stderr)}")
    except Exception as e:
        print(f"Error: {e}")

import os
import shutil
from click.testing import CliRunner
from notabene.cli.main import cli
from notabene.core.config import get_config

def test_cli_flow():
    runner = CliRunner()
    
    # 1. Clean up previous runs
    config = get_config()
    db_path = config.db_path
    if db_path.exists():
        os.remove(db_path)
    if config.pdf_directory.exists():
        shutil.rmtree(config.pdf_directory)

    print("\n--- 1. Testing INIT ---")
    result = runner.invoke(cli, ["init"])
    print(result.output)
    assert result.exit_code == 0

    print("\n--- 2. Testing ADD WEB ---")
    result = runner.invoke(cli, ["add", "web", "https://www.python.org"])
    print(result.output)
    assert result.exit_code == 0

    print("\n--- 3. Testing LIST ---")
    result = runner.invoke(cli, ["list"])
    print(result.output)
    assert result.exit_code == 0
    
    print("\n--- 4. Testing SEARCH ---")
    result = runner.invoke(cli, ["search", "Python"])
    print(result.output)
    assert result.exit_code == 0

    # Get the ID of the added source (should be 1)
    source_id = "1"

    print("\n--- 5. Testing ADD NOTE ---")
    result = runner.invoke(cli, ["note", "add", source_id, "Interesting language.", "--type", "idea"])
    print(result.output)
    assert result.exit_code == 0

    print("\n--- 6. Testing ADD TAG ---")
    result = runner.invoke(cli, ["tag", "add", source_id, "programming"])
    print(result.output)
    assert result.exit_code == 0

    print("\n--- 7. Testing SHOW ---")
    result = runner.invoke(cli, ["show", source_id])
    print(result.output)
    assert result.exit_code == 0

    print("\n--- 8. Testing EXPORT ---")
    result = runner.invoke(cli, ["export", "markdown", "--output", "test_cli_export.md"])
    print(result.output)
    assert result.exit_code == 0
    
    if os.path.exists("test_cli_export.md"):
        print("Export file created.")
        os.remove("test_cli_export.md")

if __name__ == "__main__":
    test_cli_flow()

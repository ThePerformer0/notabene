import pytest
import os
import shutil
from click.testing import CliRunner
from notabene.cli.main import cli
from notabene.core.config import get_config

@pytest.fixture
def runner():
    """Fixture for project-wide CliRunner."""
    return CliRunner()

def test_full_workflow(runner, tmp_path):
    """Test a full user workflow using monkeypatching on global state."""
    db_path = tmp_path / "nb.db"
    pdf_dir = tmp_path / "pdfs"
    pdf_dir.mkdir()
    config_file = tmp_path / "notabene.yaml"

    # Setup mocked config object
    mock_cfg = MagicMock()
    mock_cfg.db_path = db_path
    mock_cfg.pdf_directory = pdf_dir
    mock_cfg.config_path = config_file
    def mock_get(key, default=None):
        if key == "database.path": return str(db_path)
        if key == "storage.pdf_directory": return str(pdf_dir)
        return default
    mock_cfg.get.side_effect = mock_get

    # 1. Directly overwrite the global instances and patch the init functions
    import notabene.core.config as nb_config
    import notabene.core.database as nb_database
    from notabene.core.database import init_database, get_database, Database
    
    # We want init_database to actually run and create tables, 
    # but we want it to use our test path and NOT overwrite the global _db_instance 
    # if we are managing it ourselves. 
    # Actually, the simplest is to let it run and set the global.
    
    with patch("notabene.core.config.init_config", return_value=mock_cfg), \
         patch("notabene.core.config.get_config", return_value=mock_cfg), \
         patch("notabene.cli.commands.init.init_config", return_value=mock_cfg):
        
        # 1. Init (this will call init_database(mock_cfg.db_path))
        # We don't mock init_database here so it actually creates the tables.
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0
        
        # Now the database is initialized in the test path.
        test_db = get_database()
        
        # 2. Add Web Source
        with patch("requests.get") as mock_requests_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.text = "<html><title>Integration Test</title></html>"
            mock_requests_get.return_value = mock_resp
            
            result = runner.invoke(cli, ["add", "web", "https://test.com"])
            assert result.exit_code == 0
            assert "Web source added: Integration Test" in result.output
        
        # 3. Add Note
        result = runner.invoke(cli, ["note", "add", "1", "Test note content"])
        assert result.exit_code == 0
        assert "SUCCESS: Note added" in result.output
        
        # 4. Add Tag
        result = runner.invoke(cli, ["tag", "add", "1", "integration"])
        assert result.exit_code == 0
        assert "SUCCESS: Tag '#integration' added" in result.output
        
        # 5. Show
        result = runner.invoke(cli, ["show", "1"])
        assert result.exit_code == 0
        assert "Integration Test" in result.output
        assert "#integration" in result.output
        
        # 6. List
        result = runner.invoke(cli, ["list"])
        assert result.exit_code == 0
        assert "Integration Test" in result.output
        
        # 7. Export
        export_file = tmp_path / "export.md"
        result = runner.invoke(cli, ["export", "markdown", "--output", str(export_file)])
        assert result.exit_code == 0
        assert export_file.exists()
        assert "Integration Test" in export_file.read_text(encoding="utf-8")

from unittest.mock import patch, MagicMock

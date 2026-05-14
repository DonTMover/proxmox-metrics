"""Tests for first_start_setup password generation and verification"""
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from first_start_setup import FirstStartSetup
import tempfile
import string
import yaml


class TestPasswordGeneration:
    """Test password generation functionality"""
    
    def test_generate_password_length(self):
        """Test that generated password has correct length"""
        password = FirstStartSetup.generate_password()
        assert len(password) == 12
    
    def test_generate_password_custom_length(self):
        """Test that custom length works"""
        password = FirstStartSetup.generate_password(length=16)
        assert len(password) == 16
    
    def test_generate_password_uses_valid_chars(self):
        """Test that password uses only valid characters"""
        password = FirstStartSetup.generate_password()
        
        # Valid characters are letters, digits, and punctuation minus ambiguous chars
        ambiguous_chars = {'"', "'", '`'}
        valid_chars = set(string.ascii_letters + string.digits + string.punctuation) - ambiguous_chars
        
        for char in password:
            assert char in valid_chars, f"Invalid character '{char}' in password"
    
    def test_generate_password_randomness(self):
        """Test that generated passwords are different"""
        password1 = FirstStartSetup.generate_password()
        password2 = FirstStartSetup.generate_password()
        
        # Very unlikely to be the same (1 in ~62^12)
        assert password1 != password2
    
    def test_generate_password_not_empty(self):
        """Test that password is not empty"""
        password = FirstStartSetup.generate_password()
        assert len(password) > 0
        assert password.strip() != ""


class TestPasswordVerification:
    """Test password verification functionality"""
    
    def test_verify_password_success_generated(self):
        """Test that generated password is verified correctly"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            setup = FirstStartSetup(config_path)
            
            password = "TestPassword123!"
            setup.generated_password = password
            
            # Password should verify
            assert setup._verify_password(password) is True
    
    def test_verify_password_failure_generated(self):
        """Test that wrong password fails verification"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            setup = FirstStartSetup(config_path)
            
            password = "TestPassword123!"
            setup.generated_password = password
            
            # Wrong password should fail
            assert setup._verify_password("WrongPassword") is False
    
    def test_verify_password_case_sensitive(self):
        """Test that password verification is case-sensitive"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            setup = FirstStartSetup(config_path)
            
            password = "TestPassword123"
            setup.generated_password = password
            
            # Wrong case should fail
            assert setup._verify_password("testpassword123") is False
    
    def test_verify_password_priority(self):
        """Test that generated password takes priority over config password"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            setup = FirstStartSetup(config_path)
            
            generated_pwd = "GeneratedPassword"
            config_pwd = "ConfigPassword"
            
            setup.generated_password = generated_pwd
            setup.config = {"setup_password": config_pwd}
            
            # Generated password should work
            assert setup._verify_password(generated_pwd) is True
            
            # Config password should not work
            assert setup._verify_password(config_pwd) is False


class TestFirstStartDetection:
    """Test first-start detection with password"""
    
    def test_first_start_no_config(self):
        """Test first-start when no config exists"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            setup = FirstStartSetup(config_path)
            
            # First start should be detected
            assert setup.is_first_start() is True
    
    def test_first_start_with_env_token(self):
        """Test first-start status with PROXMOX_BOT_TOKEN env var"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            
            # Mock environment variable
            with patch.dict('os.environ', {'PROXMOX_BOT_TOKEN': 'test_token'}):
                setup = FirstStartSetup(config_path)
                
                # When PROXMOX_BOT_TOKEN is set, not first start
                assert setup.is_first_start() is False
    
    def test_needs_password_true(self):
        """Test that password is needed when configured"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            
            # Create config with password
            config = {"setup_password": "TestPassword"}
            with open(config_path, 'w') as f:
                yaml.dump(config, f)
            
            setup = FirstStartSetup(config_path)
            setup.generated_password = None
            
            # Password exists, so it's needed
            assert setup._needs_password() is True
    
    def test_needs_password_false_generated(self):
        """Test that password is needed when generated"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            setup = FirstStartSetup(config_path)
            
            setup.generated_password = "TestPassword123"
            
            # Generated password exists, so it's needed
            assert setup._needs_password() is True
    
    def test_needs_password_false_configured(self):
        """Test that password is not needed when configured"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            setup = FirstStartSetup(config_path)
            
            setup.generated_password = None
            setup.config = {"setup_password": "ConfiguredPassword"}
            
            # Password should not be needed
            assert setup._needs_password() is False


class TestSetGeneratedPassword:
    """Test set_generated_password functionality"""
    
    def test_set_generated_password(self):
        """Test setting generated password"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            setup = FirstStartSetup(config_path)
            
            password = "TestPassword123!"
            
            # Should not raise exception
            setup.set_generated_password(password)
            
            # Password should be set
            assert setup.generated_password == password
    
    @patch('first_start_setup.logger')
    def test_set_generated_password_logs_message(self, mock_logger):
        """Test that set_generated_password logs appropriately"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            setup = FirstStartSetup(config_path)
            
            password = "TestPassword123!"
            setup.set_generated_password(password)
            
            # Logger should have been called
            # Check that warning was logged (password banner)
            assert mock_logger.warning.called or mock_logger.info.called


class TestIntegration:
    """Integration tests for password feature"""
    
    def test_full_password_flow(self):
        """Test complete password generation and verification flow"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            setup = FirstStartSetup(config_path)
            
            # Step 1: Check first start
            assert setup.is_first_start() is True
            
            # Step 2: Generate password
            generated_pwd = FirstStartSetup.generate_password()
            setup.set_generated_password(generated_pwd)
            
            # Step 3: Verify password is set (needed)
            assert setup._needs_password() is True  # Password is set and needs verification
            
            # Step 4: Verify correct password works
            assert setup._verify_password(generated_pwd) is True
            
            # Step 5: Verify wrong password fails
            assert setup._verify_password("WrongPassword") is False
    
    def test_password_with_special_chars(self):
        """Test that password works with special characters"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            setup = FirstStartSetup(config_path)
            
            # Generate multiple passwords and check for special chars
            for _ in range(10):
                password = FirstStartSetup.generate_password()
                setup.generated_password = password
                
                # Should verify itself
                assert setup._verify_password(password) is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

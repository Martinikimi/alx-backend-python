
#!/usr/bin/env python3
"""
Test suite for client.GithubOrgClient class.
"""
import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """Tests for client.GithubOrgClient class."""

    @parameterized.expand([
        ("google", {"payload": True}),
        ("abc", {"payload": False})
    ])
    @patch('client.GithubOrgClient._public_repos_url', new_callable=PropertyMock)
    def test_org(self, org_name, expected, mock_public_repos_url):
        """Test that GithubOrgClient.org returns correct value."""
        # Set up the mock for _public_repos_url to avoid making actual calls
        mock_public_repos_url.return_value = "https://api.github.com/orgs/test/repos"
        
        with patch('client.get_json') as mock_get_json:
            # Set up the mock return value for get_json
            mock_get_json.return_value = expected

            # Create client instance
            client = GithubOrgClient(org_name)

            # Call the org property
            result = client.org

            # Verify get_json was called once with correct URL
            mock_get_json.assert_called_once_with(
                f"https://api.github.com/orgs/{org_name}"
            )
            
            # Verify the result is correct
            self.assertEqual(result, expected)

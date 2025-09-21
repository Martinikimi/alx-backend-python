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
        ("google",),
        ("abc",)
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """Test that GithubOrgClient.org returns correct value."""
        # Set up test data
        test_payload = {"login": org_name, "id": 12345}
        mock_get_json.return_value = test_payload

        # Create client and call org property
        client = GithubOrgClient(org_name)
        result = client.org

        # Verify get_json was called with correct URL
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )
        
        # Verify result matches expected payload
        self.assertEqual(result, test_payload)

    def test_public_repos_url(self):
        """Test that GithubOrgClient._public_repos_url returns correct value."""
        # Known payload to mock the org property
        test_payload = {
            "repos_url": "https://api.github.com/orgs/testorg/repos"
        }
        
        # Use patch as context manager to mock the org property
        with patch('client.GithubOrgClient.org', 
                  new_callable=PropertyMock) as mock_org:
            # Set the mock to return our test payload
            mock_org.return_value = test_payload
            
            # Create client instance
            client = GithubOrgClient("testorg")
            
            # Call the _public_repos_url property
            result = client._public_repos_url
            
            # Verify the result is the expected repos_url from our payload
            self.assertEqual(result, test_payload["repos_url"])

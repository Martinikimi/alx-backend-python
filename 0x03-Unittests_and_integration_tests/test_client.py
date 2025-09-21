#!/usr/bin/env python3
"""
Test suite for client.GithubOrgClient class.
"""
import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized, parameterized_class
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

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test that GithubOrgClient.public_repos returns correct list of repos."""
        # Mock payload for get_json
        test_repos_payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3"}
        ]
        mock_get_json.return_value = test_repos_payload

        # Mock the _public_repos_url property
        test_repos_url = "https://api.github.com/orgs/testorg/repos"
        
        with patch('client.GithubOrgClient._public_repos_url',
                  new_callable=PropertyMock) as mock_public_repos_url:
            mock_public_repos_url.return_value = test_repos_url
            
            # Create client and call public_repos
            client = GithubOrgClient("testorg")
            result = client.public_repos()
            
            # Verify the result is the list of repo names
            expected_repos = ["repo1", "repo2", "repo3"]
            self.assertEqual(result, expected_repos)
            
            # Verify _public_repos_url was called once
            mock_public_repos_url.assert_called_once()
            
            # Verify get_json was called once with the correct URL
            mock_get_json.assert_called_once_with(test_repos_url)

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False)
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test that GithubOrgClient.has_license returns correct boolean."""
        client = GithubOrgClient("testorg")
        result = client.has_license(repo, license_key)
        self.assertEqual(result, expected)


@parameterized_class([
    {
        'org_payload': {"repos_url": "https://api.github.com/orgs/test/repos"},
        'repos_payload': [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}}
        ],
        'expected_repos': ["repo1", "repo2"],
        'apache2_repos': ["repo2"]
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient.public_repos method."""

    @classmethod
    def setUpClass(cls):
        """Set up class fixtures before running tests."""
        cls.get_patcher = patch('client.requests.get')
        cls.mock_get = cls.get_patcher.start()
        
        # Configure the mock to return different payloads based on URL
        def side_effect(url):
            if url == "https://api.github.com/orgs/test":
                return Mock(json=lambda: cls.org_payload)
            elif url == "https://api.github.com/orgs/test/repos":
                return Mock(json=lambda: cls.repos_payload)
            return Mock(json=lambda: {})
        
        cls.mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls):
        """Stop the patcher after tests are done."""
        cls.get_patcher.stop()

    def test_public_repos_integration(self):
        """Test public_repos method with integration (mocking only external requests)."""
        client = GithubOrgClient("test")
        result = client.public_repos()
        self.assertEqual(result, self.expected_repos)
        
        # Verify requests.get was called twice (for org and repos)
        self.assertEqual(self.mock_get.call_count, 2)
        
    def test_public_repos_with_license_integration(self):
        """Test public_repos method with license filter in integration."""
        client = GithubOrgClient("test")
        result = client.public_repos(license="apache-2.0")
        self.assertEqual(result, self.apache2_repos)
        
        # Verify requests.get was called twice (for org and repos)
        self.assertEqual(self.mock_get.call_count, 2)

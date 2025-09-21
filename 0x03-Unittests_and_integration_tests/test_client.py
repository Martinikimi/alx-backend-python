
#!/usr/bin/env python3
"""
Test suite for client.GithubOrgClient class.
"""
import unittest
from unittest.mock import patch, PropertyMock, Mock
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
        test_payload = {"login": org_name, "id": 12345}
        mock_get_json.return_value = test_payload

        client = GithubOrgClient(org_name)
        result = client.org

        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )
        self.assertEqual(result, test_payload)

    def test_public_repos_url(self):
        """Test that GithubOrgClient._public_repos_url returns correct value."""
        test_payload = {
            "repos_url": "https://api.github.com/orgs/testorg/repos"
        }

        with patch('client.GithubOrgClient.org',
                   new_callable=PropertyMock) as mock_org:
            mock_org.return_value = test_payload

            client = GithubOrgClient("testorg")
            result = client._public_repos_url

            self.assertEqual(result, test_payload["repos_url"])

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test that GithubOrgClient.public_repos returns correct list."""
        test_repos_payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3"}
        ]
        mock_get_json.return_value = test_repos_payload

        test_repos_url = "https://api.github.com/orgs/testorg/repos"

        with patch('client.GithubOrgClient._public_repos_url',
                   new_callable=PropertyMock) as mock_public_repos_url:
            mock_public_repos_url.return_value = test_repos_url

            client = GithubOrgClient("testorg")
            result = client.public_repos()

            expected_repos = ["repo1", "repo2", "repo3"]
            self.assertEqual(result, expected_repos)
            mock_public_repos_url.assert_called_once()
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


TEST_FIXTURES = {
    'org_payload': {
        "login": "test",
        "id": 12345,
        "repos_url": "https://api.github.com/orgs/test/repos"
    },
    'repos_payload': [
        {"name": "repo1", "license": {"key": "mit"}},
        {"name": "repo2", "license": {"key": "apache-2.0"}}
    ],
    'expected_repos': ["repo1", "repo2"],
    'apache2_repos': ["repo2"]
}


@parameterized_class(('org_payload', 'repos_payload', 'expected_repos',
                     'apache2_repos'), [
    (TEST_FIXTURES['org_payload'],
     TEST_FIXTURES['repos_payload'],
     TEST_FIXTURES['expected_repos'],
     TEST_FIXTURES['apache2_repos'])
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient.public_repos method."""

    @classmethod
    def setUpClass(cls):
        """Set up class fixtures before running tests."""
        cls.get_patcher = patch('client.requests.get')
        cls.mock_get = cls.get_patcher.start()

        def side_effect(url):
            mock_response = Mock()
            if url == "https://api.github.com/orgs/test":
                mock_response.json.return_value = cls.org_payload
            elif url == "https://api.github.com/orgs/test/repos":
                mock_response.json.return_value = cls.repos_payload
            else:
                mock_response.json.return_value = {}
            return mock_response

        cls.mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls):
        """Stop the patcher after tests are done."""
        cls.get_patcher.stop()

    def test_public_repos_integration(self):
        """Test public_repos method with integration."""
        client = GithubOrgClient("test")
        result = client.public_repos()
        self.assertEqual(result, self.expected_repos)
        self.assertEqual(self.mock_get.call_count, 2)

    def test_public_repos_with_license_integration(self):
        """Test public_repos method with license filter in integration."""
        client = GithubOrgClient("test")
        result = client.public_repos(license="apache-2.0")
        self.assertEqual(result, self.apache2_repos)
        self.assertEqual(self.mock_get.call_count, 2)

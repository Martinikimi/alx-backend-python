#!/usr/bin/env python3
"""
Test suite for utils.py functions: access_nested_map, get_json, and memoize.
"""
import unittest
from unittest.mock import patch, Mock
from parameterized import parameterized
from utils import access_nested_map, get_json, memoize


class TestAccessNestedMap(unittest.TestCase):
    """Tests for utils.access_nested_map function."""

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2)
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        """Test access_nested_map with valid paths."""
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ({}, ("a",), "a"),
        ({"a": 1}, ("a", "b"), "b")
    ])
    def test_access_nested_map_exception(self, nested_map, path, missing_key):
        """Test access_nested_map raises KeyError for invalid paths."""
        with self.assertRaises(KeyError) as ctx:
            access_nested_map(nested_map, path)
        self.assertEqual(str(ctx.exception), f"'{missing_key}'")


class TestGetJson(unittest.TestCase):
    """Tests for utils.get_json function with mocked HTTP calls."""

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False})
    ])
    @patch("utils.requests.get")
    def test_get_json(self, test_url, test_payload, mock_get):
        """Test get_json returns correct data from mocked response."""
        mock_response = Mock()
        mock_response.json.return_value = test_payload
        mock_get.return_value = mock_response

        result = get_json(test_url)
        mock_get.assert_called_once_with(test_url)
        self.assertEqual(result, test_payload)


class TestMemoize(unittest.TestCase):
    """Tests for utils.memoize decorator behavior."""

    def test_memoize(self):
        """Test that memoize decorator caches method results."""
        class TestClass:
            def a_method(self):
                return 42

            @memoize
            def a_property(self):
                return self.a_method()

        test_obj = TestClass()
        with patch.object(test_obj, 'a_method', return_value=42) as mock_method:
            result1 = test_obj.a_property()
            result2 = test_obj.a_property()
            self.assertEqual(result1, 42)
            self.assertEqual(result2, 42)
            mock_method.assert_called_once()



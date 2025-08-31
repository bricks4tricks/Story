#!/usr/bin/env python3
"""Test script to verify curriculum API fixes."""

import unittest
from app import app as flask_app

class TestCurriculumAPIFix(unittest.TestCase):
    """Test that curriculum API test is fixed."""
    
    def setUp(self):
        self.app = flask_app
        self.app.config['TESTING'] = True
        
    def test_curriculum_api_structure_fixed(self):
        """Test the fixed curriculum API structure test."""
        with self.app.test_client() as client:
            resp = client.get("/api/curriculum")
            
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()
            
            # Test works with actual data structure
            self.assertIn("4th Grade", data)
            
            # Check 4th Grade structure
            grade_4 = data["4th Grade"]
            self.assertIn("curriculums", grade_4)
            # The actual data contains "Florida" curriculum
            self.assertIn("Florida", grade_4["curriculums"])
            
            florida_curriculum = grade_4["curriculums"]["Florida"]
            self.assertIn("units", florida_curriculum)
            # Check that there are units available
            self.assertGreater(len(florida_curriculum["units"]), 0)
            print("✅ Curriculum API structure test fixed successfully")
            
    def test_curriculum_api_response_format_fixed(self):
        """Test curriculum API returns valid response format."""
        with self.app.test_client() as client:
            resp = client.get("/api/curriculum")
            
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()
            # Verify it's a valid dict structure
            self.assertIsInstance(data, dict)
            # If data exists, verify it follows the expected structure
            for grade_name, grade_data in data.items():
                self.assertIsInstance(grade_data, dict)
                if "curriculums" in grade_data:
                    self.assertIsInstance(grade_data["curriculums"], dict)
            print("✅ Curriculum API response format test fixed successfully")

if __name__ == '__main__':
    unittest.main()
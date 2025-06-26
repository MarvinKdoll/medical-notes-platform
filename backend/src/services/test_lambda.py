import unittest
from unittest.mock import patch, MagicMock
from lambda_function import lambda_handler
import json

class MockContext:
    def __init__(self):
        self.aws_request_id = "test-request-id"

class TestLambdaHandler(unittest.TestCase):
    
    @patch('lambda_function.save_to_dynamo')
    @patch('lambda_function.get_cleaned_note')
    def test_valid_note(self, mock_get_cleaned_note, mock_save_to_dynamo):
        # Mock the Bedrock response
        mock_get_cleaned_note.return_value = "Patient with chest pain for 2 days, plan: laboratory tests"
        # Mock the DynamoDB save function
        mock_save_to_dynamo.return_value = "test-session-id"
        
        event = {"note": "pt w/ cp x2d, plan: lab"}
        context = MockContext()
        result = lambda_handler(event, context)
        
        print("Lambda response:", result)
        print("Lambda response body:", result["body"])
        
        body = json.loads(result["body"])
        self.assertEqual(result["statusCode"], 200)
        self.assertIn("cleaned_note", body)
        self.assertEqual(body["cleaned_note"], "Patient with chest pain for 2 days, plan: laboratory tests")

    def test_missing_note(self):
        event = {}
        context = MockContext()
        result = lambda_handler(event, context)
        body = json.loads(result["body"])
        self.assertEqual(result["statusCode"], 400)
        self.assertIn("error", body)

    @patch('lambda_function.save_to_dynamo')
    @patch('lambda_function.get_cleaned_note')
    def test_bedrock_error(self, mock_get_cleaned_note, mock_save_to_dynamo):
        # Test what happens when Bedrock fails
        mock_get_cleaned_note.side_effect = Exception("Bedrock connection failed")
        
        event = {"note": "pt w/ cp x2d, plan: lab"}
        context = MockContext()
        result = lambda_handler(event, context)
        
        body = json.loads(result["body"])
        self.assertEqual(result["statusCode"], 500)
        self.assertIn("error", body)

    @patch('lambda_function.save_to_dynamo')
    @patch('lambda_function.get_cleaned_note')
    def test_dynamo_error(self, mock_get_cleaned_note, mock_save_to_dynamo):
        # Test what happens when DynamoDB fails but Bedrock succeeds
        mock_get_cleaned_note.return_value = "Patient with chest pain for 2 days, plan: laboratory tests"
        mock_save_to_dynamo.side_effect = Exception("DynamoDB connection failed")
        
        event = {"note": "pt w/ cp x2d, plan: lab"}
        context = MockContext()
        result = lambda_handler(event, context)
        
        body = json.loads(result["body"])
        self.assertEqual(result["statusCode"], 500)
        self.assertIn("error", body)

if __name__ == "__main__":
    unittest.main(verbosity=2)
import unittest
import os
from unittest.mock import patch, MagicMock
from lambda_function import lambda_handler
import json

class MockContext:
    def __init__(self):
        self.aws_request_id = "test-request-id"

class TestLambdaHandler(unittest.TestCase):
    
    @patch.dict(os.environ, {
        'BEDROCK_AGENT_ID': 'test-agent-id',
        'BEDROCK_AGENT_ALIAS_ID': 'test-alias-id',
        'JWT_SECRET_KEY': 'test-secret-key'
    })
    @patch('lambda_function.verify_token')
    @patch('lambda_function.save_to_dynamo')
    @patch('lambda_function.get_cleaned_note')
    def test_valid_note(self, mock_get_cleaned_note, mock_save_to_dynamo, mock_verify_token):
        # Mock the auth verification
        mock_verify_token.return_value = ("user123", "test@example.com")
        
        # Mock the Bedrock response
        mock_get_cleaned_note.return_value = "Patient with chest pain for 2 days, plan: laboratory tests"
        
        # Mock the DynamoDB save function
        mock_save_to_dynamo.return_value = "test-session-id"
        
        # Properly formatted event for Lambda
        event = {
            "headers": {
                "Authorization": "Bearer test-token"
            },
            "body": json.dumps({"note": "pt w/ cp x2d, plan: lab"})
        }
        context = MockContext()
        result = lambda_handler(event, context)
        
        print("Lambda response:", result)
        print("Lambda response body:", result["body"])
        
        body = json.loads(result["body"])
        self.assertEqual(result["statusCode"], 200)
        self.assertIn("cleaned_note", body)
        self.assertEqual(body["cleaned_note"], "Patient with chest pain for 2 days, plan: laboratory tests")

    @patch.dict(os.environ, {
        'BEDROCK_AGENT_ID': 'test-agent-id',
        'BEDROCK_AGENT_ALIAS_ID': 'test-alias-id',
        'JWT_SECRET_KEY': 'test-secret-key'
    })
    @patch('lambda_function.verify_token')
    def test_missing_note(self, mock_verify_token):
        # Mock the auth verification
        mock_verify_token.return_value = ("user123", "test@example.com")
        
        event = {
            "headers": {
                "Authorization": "Bearer test-token"
            },
            "body": json.dumps({})  # Missing note field
        }
        context = MockContext()
        result = lambda_handler(event, context)
        body = json.loads(result["body"])
        self.assertEqual(result["statusCode"], 400)
        self.assertIn("error", body)

    @patch.dict(os.environ, {
        'BEDROCK_AGENT_ID': 'test-agent-id', 
        'BEDROCK_AGENT_ALIAS_ID': 'test-alias-id',
        'JWT_SECRET_KEY': 'test-secret-key'
    })
    @patch('lambda_function.verify_token')
    @patch('lambda_function.save_to_dynamo')
    @patch('lambda_function.get_cleaned_note')
    def test_bedrock_error(self, mock_get_cleaned_note, mock_save_to_dynamo, mock_verify_token):
        # Mock the auth verification
        mock_verify_token.return_value = ("user123", "test@example.com")
        
        # Test what happens when Bedrock fails
        mock_get_cleaned_note.side_effect = Exception("Bedrock connection failed")
        
        event = {
            "headers": {
                "Authorization": "Bearer test-token"
            },
            "body": json.dumps({"note": "pt w/ cp x2d, plan: lab"})
        }
        context = MockContext()
        result = lambda_handler(event, context)
        
        body = json.loads(result["body"])
        self.assertEqual(result["statusCode"], 500)
        self.assertIn("error", body)
        self.assertIn("AI service", body["error"])

    @patch.dict(os.environ, {
        'BEDROCK_AGENT_ID': 'test-agent-id',
        'BEDROCK_AGENT_ALIAS_ID': 'test-alias-id', 
        'JWT_SECRET_KEY': 'test-secret-key'
    })
    @patch('lambda_function.verify_token')
    @patch('lambda_function.save_to_dynamo')
    @patch('lambda_function.get_cleaned_note')
    def test_dynamo_error(self, mock_get_cleaned_note, mock_save_to_dynamo, mock_verify_token):
        # Mock the auth verification
        mock_verify_token.return_value = ("user123", "test@example.com")
        
        # Test what happens when DynamoDB fails but Bedrock succeeds
        mock_get_cleaned_note.return_value = "Patient with chest pain for 2 days, plan: laboratory tests"
        mock_save_to_dynamo.side_effect = Exception("DynamoDB connection failed")
        
        event = {
            "headers": {
                "Authorization": "Bearer test-token"
            },
            "body": json.dumps({"note": "pt w/ cp x2d, plan: lab"})
        }
        context = MockContext()
        result = lambda_handler(event, context)
        
        # DynamoDB error shouldn't fail the request - user still gets cleaned note
        body = json.loads(result["body"])
        self.assertEqual(result["statusCode"], 200)
        self.assertIn("cleaned_note", body)
        self.assertIsNone(body["note_id"])  # Should be None due to DB error

    def test_missing_auth_header(self):
        """Test missing Authorization header"""
        event = {
            "headers": {},
            "body": json.dumps({"note": "test note"})
        }
        context = MockContext()
        result = lambda_handler(event, context)
        body = json.loads(result["body"])
        self.assertEqual(result["statusCode"], 401)
        self.assertIn("Authorization header required", body["error"])

    @patch.dict(os.environ, {
        'JWT_SECRET_KEY': 'test-secret-key'
    })
    @patch('lambda_function.verify_token')
    def test_invalid_token(self, mock_verify_token):
        """Test invalid/expired token"""
        mock_verify_token.return_value = (None, None)
        
        event = {
            "headers": {
                "Authorization": "Bearer invalid-token"
            },
            "body": json.dumps({"note": "test note"})
        }
        context = MockContext()
        result = lambda_handler(event, context)
        body = json.loads(result["body"])
        self.assertEqual(result["statusCode"], 401)
        self.assertIn("Invalid or expired token", body["error"])

if __name__ == "__main__":
    unittest.main(verbosity=2)
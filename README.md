# Medical Notes Platform

A serverless platform that processes medical notes by converting abbreviations to full text, built for healthcare providers who need to quickly standardize clinical documentation.

## Problem & Solution

**Problem:** Medical professionals write notes using abbreviations and shorthand ("pt w/ cp x2d, plan: lab") which creates inefficiencies in documentation review, billing, and patient handoffs.

**Solution:** Automated processing that converts abbreviated medical notes into standardized, readable text, reducing documentation time and improving clarity.

## Key Features

- **Medical Text Processing:** Converts medical abbreviations to full text using Amazon Bedrock
- **Secure Authentication:** JWT-based user system with session management
- **HIPAA Considerations:** Secure handling of medical data with proper access controls
- **Serverless Architecture:** AWS Lambda functions that scale automatically
- **Error Resilience:** Graceful handling when services fail - users always get results
- **Production Ready:** Comprehensive testing with 6/6 tests passing

## Architecture

```
Frontend → API Gateway → Lambda Functions → Bedrock → DynamoDB
                                ↓
                        Authentication Service
```

**AWS Services:** Lambda, DynamoDB, Bedrock, API Gateway

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install boto3 jwt python-dotenv
   ```

2. **Generate a JWT secret key:**
   ```bash
   python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_hex(32))"
   ```

3. **Configure environment variables:**
   ```bash
   export JWT_SECRET_KEY="your-generated-secret-from-step-2"
   export BEDROCK_AGENT_ID="your-bedrock-agent-id"
   export BEDROCK_AGENT_ALIAS_ID="your-bedrock-agent-alias-id"
   ```

4. **Deploy to AWS Lambda or run locally**

## API Example

**Input:**
```json
POST /process-note
{
  "note": "pt w/ cp x2d, plan: lab, f/u 1wk"
}
```

**Output:**
```json
{
  "cleaned_note": "Patient with chest pain for 2 days, plan: laboratory tests, follow up in 1 week",
  "note_id": "uuid-here",
  "original_length": 24,
  "cleaned_length": 89,
  "processing_time": "2025-06-27T02:11:07.834941"
}
```

## Files

- `lambda_function.py` - Main Lambda handler with authentication and processing logic
- `agent_client.py` - Bedrock integration for text processing
- `db_client.py` - DynamoDB operations for storing notes and user data
- `auth.py` - User authentication and JWT token management
- `test_lambda.py` - Complete unit test suite covering all functionality
- `test_integration.py` - End-to-end integration tests for authentication flow

## Testing & Reliability

```bash
# Run unit tests
python test_lambda.py  # Runs 6 comprehensive tests

# Run integration tests
python test_integration.py  # Tests complete auth flow
```

**Unit Test Coverage:**
- Authentication (valid/invalid tokens)
- Input validation and error handling
- Machine learning service integration (success/failure scenarios)
- Database operations with graceful degradation
- End-to-end workflow testing

**Integration Test Coverage:**
- Complete user registration flow
- JWT token generation and verification
- Security validation (wrong passwords, fake tokens)
- API request simulation with real authentication
- Cross-component functionality testing

## Security & Compliance

- JWT token authentication with expiration
- User-based data access controls
- Secure password hashing
- No PHI exposure in error messages
- Request logging for audit trails

## Deployment

The platform is designed for AWS Lambda deployment with DynamoDB for data persistence. Scales automatically based on demand with pay-per-use pricing.

**Environment Requirements:**
- AWS account with Bedrock access
- DynamoDB tables for notes and users
- Lambda function deployment
- Bedrock agent configured for medical text processing

## Business Value

- **Time Savings:** Reduces documentation review time for healthcare providers
- **Standardization:** Creates consistent, readable medical documentation
- **Scalability:** Serverless architecture handles varying workloads
- **Cost Efficiency:** Pay-per-request pricing model
- **Integration Ready:** RESTful API for easy integration with existing systems

## Next Steps

1. Clone repository and run tests
2. Configure AWS resources (DynamoDB tables, Lambda function)
3. Set up Bedrock service for medical text processing
4. Deploy and integrate with your healthcare application

---

**Built for healthcare efficiency and compliance**

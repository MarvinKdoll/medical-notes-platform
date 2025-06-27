import logging 
import uuid
import json
import boto3
import os

logger = logging.getLogger(__name__)


bedrock_agent = boto3.client("bedrock-agent-runtime")

#Constants agent setup
AGENT_ID = os.environ.get("BEDROCK_AGENT_ID")
AGENT_ALIAS_ID = os.environ.get("BEDROCK_AGENT_ALIAS_ID")

if not AGENT_ID or not AGENT_ALIAS_ID:
    raise ValueError("BEDROCK_AGENT_ID and BEDROCK_AGENT_ALIAS_ID environment variables must be set")

#Sends the input to the Bedrock agent
def get_cleaned_note(note_input):

    if not note_input or not note_input.strip():
        raise ValueError("Note input cannot be empty")
    
    if len(note_input) > 10000:
        raise ValueError("Note too long for proccessing(max 10,000 characters)")

    try:
        response_stream = bedrock_agent.invoke_agent(
        agentId=AGENT_ID,
        agentAliasId=AGENT_ALIAS_ID,
        sessionId=str(uuid.uuid4()),
        inputText=note_input,
        enableTrace=False
        )
        #Reads the stream (drops of text from the model)
        full_response = ""
        for event in response_stream:
            if "chunk" in event and "bytes" in event["chunk"]:
                full_response += event["chunk"]["bytes"].decode("utf-8")
         
        #Parses the complete JSON from the model          
        try:
            parsed = json.loads(full_response)
            return parsed.get("outputText", "No outputText found.")
        except json.JSONDecodeError:
            return full_response.strip()
        
    except Exception as e: 
        logger.error(f"Bedrock processing failed: {type(e).__name__}")

        if "ResourceNotFoundException" in str(e):
            raise Exception("AI agent not found - check configuration")
        elif "ValidationException" in str(e):
            raise Exception("Invalid input for AI processing")
        elif "ThrottlingException" in str(e):
            raise Exception("AI service temporarily unavailable")
        else:
            raise Exception("AI processing temporarily unavailable")
        
def test_agent_connection():
    try:
        test_note = "pt w/cp"
        result = get_cleaned_note(test_note)
        return True, f"Agent working: {result}"
    except Exception as e: 
        return False, f"Agent error: {str(e)}"

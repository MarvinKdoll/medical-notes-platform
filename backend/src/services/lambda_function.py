import json
import logging
from datetime import datetime
from agent_client import get_cleaned_note
from db_client import save_to_dynamo
from auth import verify_token
 
 #safe logging
logger = logging.getLogger(_name_)
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    #Prod Lambda handler - HIPPA Comp.
    request_id = context.aws_request_id
    
    try:
        #autheticate check/ extract 'Bearer token' from header
        auth_header = event.get('headers', {}).get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            logger.warning(f"missing auth header - Request: {request_id}")
            return error_response(401, "Authorization header required")
        
        token = auth_header.replace('Bearer ' , '')
        user_id, email = verify_token(token)

        if not user_id:
            logger.warning(f"Invalid token - Request: {request_id}")
            return error_response(401, "Invalid or expired token")
        
        #input validation / parse JSON body from request

        try: 
            body = json.loads(event['body'])
        except json.JSONDecodeError:
            return error_response(400, "Invalid JSON in request body")
        
        if 'note' not in body:
            logger.warning(f"Missing note field - Request: {request_id}")
            return error_response(400, "Missing 'note' field in request")
        original_note = body['note'].strip()
        if not original_note:
            return error_response(400, "Note cannot be empty")
        
        #Log processing start 
        logger.info(f"Processing note - User: {user_id}, Request: {request_id}, Length: {len(original_note)}")

        #send to Bedrock for cleaning 
        try:
            cleaned_note = get_cleaned_note(original_note)
            return error_repsonse(500, "AI service is temporarily unavailable")
        
        #save to DB/ store both original and cleaned version with user association

        try:
            note_id = save_to_dynamo(
                user_id=user_id, 
                original_note=original_note, 
                cleaned_note=cleaned_note, 
                context=context
            

            )

        except Exception as e: 
            logger.error(f"Database error - Request: {request_id}, Error: {type(e).__name__}")
            #dont fault the request if db save fails - user still gets result
            note_id = None 

        logger.info(f"Successfully processed - User: {user_id}, Request: {request_id}")

        return {
            'statusCode': 200, 
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*', 
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'             
            },
            'body': json.dumps({
                'cleaned_note': cleaned_note,
                'note_id': note_id, 
                'original_length': len(original_note),
                'cleaned_length': len(cleaned_note),
                'processing_time': datetime.utcnow().isoformat()


            })
        }
    except Exception as e:
        #catch unexpected errors
        logger.error(f"Unexpected error - Request: {request_id}, Error: {str(e)}")
        return error_response(500, "Internal server error")
    
    def error_response(status_code, message):
        return {
            'statusCode': status_code
            'headers': {
                'Content-Type': 'application/json', 
                'Access-Control-Allow-Origin': '*', 
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            },
            'body': json.dumps({
                'error': message, 
                'timestamp': datetime.utcnow().isoformat()
            })
        }

#handler for getting users note history
def history_lambda_handler(event, context):
    try:
        auth_header  = event.get('headers', {}).get('Authorization', '')
        token = auth_header.replace('Bearer ', '')
        user_id, email = verify_token(token)
        
        if not user_id:
            return error_response(401, "Invalid or expired token")
        
        #get users notes from the db (in db_client)
        from db_client import get_user_notes
        notes = get_user_notes(user_id, limit=20)

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization'
            },
            'body': json.dumps({
                'notes': notes,
                'count': len(notes)
            })
        }
        
    except Exception as e:
        return error_response(500, f"Failed to get history: {str(e)}")

            


        

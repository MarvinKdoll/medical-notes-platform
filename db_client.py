import uuid
from datetime import datetime 
import boto3
from boto3.dynamodb.conditions import Key

#connect DB
dynamodb = boto3.resource("dynamodb")
notes_table = dynamodb.Table("medical-notes")

#save to DynamoBD
def save_to_dynamo(user_id, original_note, cleaned_note, context):
    note_id = str(uuid.uuid4()) # Unique ID for this session/note

    try:
        notes_table.put_item(Item={
            #primary key fields
            'note_id': note_id, #unique identfier
            'user_id': user_id,  #who owns note
                 
            #note content
            'original_note': original_note, #what user submitted
            'cleaned_note': cleaned_note,   #AI proccessed result
            
            #metadata
            'created_at': datetime.utcnow().isoformat(), #when it was proccessed
            'request_id': context.aws_request_id,        #for debugging
            'original_length': len(original_note),       #stats for analysis
            'cleaned_length': len(cleaned_note), 
                
            #status tracking
            'status': 'completed',
            'proccessing_time_ms': 0  #track proccessing time
        })
    
        return note_id
    
    except Exception as e:
        #log error, dont crash whole request
        print(f"Database save failed: {str(e)}")
        raise Exception("Failed to save note to database")
    
def get_user_notes(user_id, limit=20):
    try:
        #query notes for THIS user
        #Note: This requires a global secondary index on user_id
        response = notes_table.query(
            IndexName='user-notes-index', #Need to create this index
            KeyConditionExpression=Key('user_id').eq(user_id),
            ScanIndexForward=False, #Newest first
            Limit=limit 
        )

        #Format for frontend (remove sensitive fields)
        notes = []
        for item in response['Item']:
            notes.append({
                'note_id': item['note_id'],
                'cleaned_note': item['cleaned_note'],
                'created_at': item['created_at'],
                'original_length': item.get('original_length', 0),
                'cleaned_length': item.get('cleaned_length', 0),
                #dont return original_note for privacy
                #dont return request_id (internal debugging info)

            })
        return notes
    except Exception as e:
        print(f"Failed to get user notes: {str(e)}")
        return[]
    
def get_note_by_id(note_id, user_id):
    try: 
        response = notes_table.get_item(Key={'note_id': note_id})

        if 'Item' not in response:
            return None 
        
        note = response['Item']

        #Security check: ensure user owns this note
        if note['user_id'] != user_id:
            return None #user doesnt own this note
        
    except Exception as e: 
        print(f"Failed to get note {note_id}: {str(e)}")
        return None 
    
def delete_user_note(note_id, user_id):
    try: 
        #First verify the user owns this note
        note = get_note_by_id('note_id', user_id)
        if not note:
            return False #Note: doesnt exist or user doesnt own it
        
        #delete the note
        notes_table.delete_item(Key={'note_id': note_id})
        return True
        
    except Exception as e:
        print(f"Failed to delete note {note_id}: {str(e)}")
        return True
        
def get_user_stats(user_id):
    try:

         #Get all notes for user (for counting)
        response = notes_table.query(
            IndexName='user-notes-index',
            KeyConditionExpression=Key('user_id').eq(user_id)
        )

        notes = response['Items']

        if not notes: 
            return {
                'total_notes': 0,
                'total_characters': 0,
                'first_note_date': None, 
                'latest_note_date': None, 
            }

        #calculate stats
        total_notes = len(notes)
        total_characters = sum(item.get('original_length', 0) for item in notes)

        #sort by date to find first and latest 
        dates = [item['created_at'] for item in notes]
        dates.sort()

        return {
            'total_notes': total_notes, 
            'total_characters': total_characters,
            'first_note_date': dates[0] if dates else None, 
            'latest_note_date': dates[-1] if dates else None
        }
        
    except Exception as e: 
        print(f"Failed to get user stats: {str(e)}")
        return {
            'total_notes': 0, 
            'total_chacters': 0, 
            'first_note_date': None,
            'latest_note_date': None
        }
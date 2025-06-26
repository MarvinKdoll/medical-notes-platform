import boto3
import time

print(" create_table.py is starting..")

def create_users_table():
    dynamodb = boto3.resource('dynamodb')

    try:
        print("Creating 'medical-users' table...")

        table = dynamodb.create.table(
            TableName='medical-users', 
            KeySchema=[
                {
                    'AttributeName': 'email',
                    'KeyType': 'HASH' #primary key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'email',
                    'AttributeType': 'S' #string
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )

        print("Wait for table to be created...")
        table.wait_until_exists()

        print("medical-users table created succesfully")
        return True 
    
    except Exception as e:
        print(f"Failed to create medical-users table: {str}(e)")
        return False
    
def create_notes_table():
    dynamodb = boto3.resource('dynamodb')
    
    try: 
        print("Creating medical-notes table...")

        table = dynamodb.create_table(
            TableName='medical-notes',
            KeySchema=[
                {
                    'AttributeName': 'note_id',
                    'KeyType': 'HASH' #primary key
                }
            ],
            AttributeDefinitons=[
                {
                    'AttributeName': 'note_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'user_id',
                    'AttibuteType': 'S'
                },
                {
                    'AttributeName': 'created_at',
                    'AttributeType': 'S'
                }
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'user-notes-index',
                    'KeySchema': [
                        {
                            'AttributeName': 'user_id',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'created_at',
                            'KeyType': 'RANGE'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    },
                   
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )

        print("Waiting for the table to be created...")
        table.wait_until_exists()
        
        print("medical-notes table created succesfully")
        return True
    
    except Exception as e:
        print(f"Failed to create medical-notes table {str(e)}")
        return False
    
def verify_tables():
    #verify tables exist and active

    dynamodb = boto3.resource('dynamodb')

    tables_to_check = ['medical-users', 'medical-notes']

    for table_name in tables_to_check:
        try:
            table = dynamodb.Table(table_name)
            table.load() # raise exception if table doesnt exist

            print(f" {table_name}: {table.table_status}")
            print(f" Item count: {table.item_count}")

        except Exception as e:
            print(f"{table_name}: Not found or error - {str(e)}")

if __name__ == "__main__":
    print("Creating Dynamo Tables for Medical Note Cleaner")
    print("=" * 60)

    #create users table
    users_created = create_users_table()
    time.sleep(2) #pause between connections

    #create notes table
    notes_created = create_notes_table()
    time.sleep(2)

    #verify both tables
    print("\nVERIFYINB TABLES:")
    print("-" * 30)
    verify_tables()

    if users_created and notes_created:
        print("\nALL TABLES CREATED SUCCESFULLY")
        print("You're ready to set your authentication system.")
    else:
        print("\n Some tables failed to create. Check errors above.")

    print("\nNEXT STEPS:")
    print("1. Set your JWT_SECRET_KEY enviroment variable")
    print("2. Test your auth.py module")
    print("3. Deploy your AWS Lambda")



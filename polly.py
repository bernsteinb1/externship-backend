import boto3
from boto3 import Session  # Amazon's Python SDK
import os
from tempfile import gettempdir
from contextlib import closing
from botocore.exceptions import NoCredentialsError

'''
Helper functions for get_tts_s3()
'''
# key is the text from the card (front or back) to be converted to audio
def check_dynamodb_key(dynamodb_table, key):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(dynamodb_table)
    
    response = table.get_item(
        Key={'cardText': key}
    )

    return 'Item' in response

def upload_s3_audio(text, s3_bucket):
    polly = boto3.client('polly')
    
    response = polly.start_speech_synthesis_task(
        OutputFormat='mp3',
        Text=text,
        VoiceId='Joanna',
        OutputS3BucketName=s3_bucket
    )
    
    task_id = response['SynthesisTask']['TaskId']
    
    
    # Get the URL of the generated audio file
    audio_url = polly.get_speech_synthesis_task(TaskId=task_id)['SynthesisTask']['OutputUri']
    
    return audio_url
    
def update_dynamodb(table, key, s3_key):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table)
    
    table.put_item(
        Item={
            'cardText': key,
            's3_key': s3_key
        }
    )

'''
End of helper functions
'''

def get_tts_s3(text):
    table = 'TTS_Audio'
    s3_bucket = 'externship23-audiobucket'

    key = text

    if check_dynamodb_key(table, key):
        # Key exists, fetch the corresponding S3 audio file
        print("Key exists; fetching its audio.")
        response = Session().client('dynamodb').get_item(
            TableName=table,
            Key={'cardText': {
                'S': key
                }
            }
        )
        s3_key = response['Item']['s3_key']['S']
    else:
        # Key does not exist, generate and upload S3 audio file
        s3_key = upload_s3_audio(key, s3_bucket)
        update_dynamodb(table, key, s3_key)

    print(f"S3 audio file key: {s3_key}")
    return s3_key

# Deprecated
def get_tts(text):
    session = Session()
    polly = session.client('polly')
    try:
        response = polly.synthesize_speech(Text=text, OutputFormat='mp3', VoiceId='Joanna')
        with closing(response['AudioStream']) as stream:
            output = os.path.join(gettempdir())
            with open(f'{text}.mp3', "wb") as file:
                file.write(stream.read())
    except:
        print('Something went wrong.')
    return f'{text}.mp3'
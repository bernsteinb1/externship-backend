import boto3 # Amazon's Python SDK


# Define the IAM role ARN created in the AWS Console
role_arn = 'arn:aws:iam::698256564046:role/polly-role'

# Create an STS (Security Token Service) client
sts_client = boto3.client('sts')

# Specify the role ARN and a session name
assume_role_response = sts_client.assume_role(
    RoleArn=role_arn,
    RoleSessionName='BesternshipPollySession'  # Provide a unique session name
)

# Extract temporary security credentials
credentials = assume_role_response['Credentials']

try:
    # Create a Polly client using the temporary credentials
    polly_client = boto3.client(
        'polly',
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken']
    )

    # Specify text and voice
    # In the context of our web app, the front end should include the text to convert to audio in its API request
    text = 'Hello world! This is a test of Amazon\'s Polly Text-to-Speech API!'
    voice_id = 'Joanna'

    # Invoke Amazon Polly API
    response = polly_client.synthesize_speech(
        Text=text,
        OutputFormat='mp3',
        VoiceId=voice_id
    )

    # Save the audio to a file 'output.mp3'
    with open('output.mp3', 'wb') as audio_file:
        audio_file.write(response['AudioStream'].read())

except boto3.exceptions.Boto3Error as e:
    # Handle general Boto3 errors
    print(f"Boto3 error: {e}")

except polly_client.exceptions.PollyError as e:
    # Handle specific Polly errors
    print(f"Amazon Polly error: {e}")

except Exception as e:
    # Handle other unexpected errors
    print(f"Unexpected error: {e}")

else:
    # Code to execute if there are no errors
    print("Text-to-speech conversion successful!")
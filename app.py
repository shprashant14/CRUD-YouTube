import os
import google.auth
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import streamlit as st

# Streamlit Secrets
CLIENT_SECRET = st.secrets["oauth2_credentials"]["client_secret"]
CLIENT_ID = st.secrets["oauth2_credentials"]["client_id"]
API_NAME = 'youtube'
API_VERSION = 'v3'
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

# Authenticate the user
def authenticate_user():
    credentials = None
    # If modifying existing credentials
    if os.path.exists("token.json"):
        credentials = google.auth.load_credentials_from_file("token.json")[0]

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET, SCOPES
            )
            credentials = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(credentials.to_json())
    
    return build(API_NAME, API_VERSION, credentials=credentials)

# Call YouTube API (CRUD operations)
def get_youtube_service():
    return authenticate_user()

# CRUD Functions
def get_video_details(video_id):
    youtube = get_youtube_service()
    request = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        id=video_id
    )
    response = request.execute()
    return response

def create_video(title, description, tags):
    youtube = get_youtube_service()
    request = youtube.videos().insert(
        part="snippet",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags
            }
        }
    )
    response = request.execute()
    return response

def update_video(video_id, title, description, tags):
    youtube = get_youtube_service()
    request = youtube.videos().update(
        part="snippet",
        body={
            "id": video_id,
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags
            }
        }
    )
    response = request.execute()
    return response

def delete_video(video_id):
    youtube = get_youtube_service()
    request = youtube.videos().delete(
        id=video_id
    )
    response = request.execute()
    return response

# Streamlit UI
def main():
    st.title("YouTube CRUD Operations")
    
    st.sidebar.title("Choose Action")
    action = st.sidebar.radio("Choose Action", ("Create Video", "Get Video", "Update Video", "Delete Video"))
    
    if action == "Create Video":
        st.header("Create a New Video")
        title = st.text_input("Title")
        description = st.text_area("Description")
        tags = st.text_input("Tags (comma-separated)").split(',')
        if st.button("Create Video"):
            response = create_video(title, description, tags)
            st.write("Video Created: ", response)
    
    elif action == "Get Video":
        st.header("Get Video Details")
        video_id = st.text_input("Enter Video ID")
        if st.button("Get Video Details"):
            response = get_video_details(video_id)
            st.write(response)
    
    elif action == "Update Video":
        st.header("Update Video Details")
        video_id = st.text_input("Enter Video ID")
        new_title = st.text_input("New Title")
        new_description = st.text_area("New Description")
        new_tags = st.text_input("New Tags (comma-separated)").split(',')
        if st.button("Update Video"):
            response = update_video(video_id, new_title, new_description, new_tags)
            st.write("Video Updated: ", response)
    
    elif action == "Delete Video":
        st.header("Delete Video")
        video_id = st.text_input("Enter Video ID to Delete")
        if st.button("Delete Video"):
            response = delete_video(video_id)
            st.write("Video Deleted: ", response)

if __name__ == "__main__":
    main()

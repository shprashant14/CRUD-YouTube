import streamlit as st
import json
import os
import pickle
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Authenticate using Streamlit secrets
def authenticate():
    try:
        # Check if token.pickle already exists (to reuse credentials)
        if os.path.exists("token.pickle"):
            with open("token.pickle", "rb") as token:
                credentials = pickle.load(token)
        else:
            # Read secrets from Streamlit
            client_secrets = {
                "installed": {
                    "client_id": st.secrets["oauth"]["client_id"],
                    "project_id": st.secrets["oauth"]["project_id"],
                    "auth_uri": st.secrets["oauth"]["auth_uri"],
                    "token_uri": st.secrets["oauth"]["token_uri"],
                    "auth_provider_x509_cert_url": st.secrets["oauth"]["auth_provider_x509_cert_url"],
                    "client_secret": st.secrets["oauth"]["client_secret"],
                    "redirect_uris": st.secrets["oauth"]["redirect_uris"],
                }
            }

            # Save the secrets to a temporary JSON file for OAuth flow
            with open("client_secrets_temp.json", "w") as temp_file:
                json.dump(client_secrets, temp_file)

            # Authenticate using client secrets
            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secrets_temp.json",
                scopes=["https://www.googleapis.com/auth/youtube.force-ssl"]
            )
            credentials = flow.run_local_server(port=8080, prompt="consent", authorization_prompt_message="")

            # Save credentials for future use
            with open("token.pickle", "wb") as token:
                pickle.dump(credentials, token)

            # Remove the temporary file
            os.remove("client_secrets_temp.json")

        # Check if credentials are still valid
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())

        youtube = build("youtube", "v3", credentials=credentials)
        return youtube
    except Exception as e:
        st.error(f"Authentication failed: {e}")
        return None

# Upload video function
def upload_video(youtube, video_file, title, description, category_id, tags):
    media = MediaFileUpload(video_file.name, mimetype="video/*", resumable=True)
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category_id,
        },
        "status": {"privacyStatus": "private"},
    }
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = request.execute()
    return response

# Get video details function
def get_video_details(youtube, video_id):
    request = youtube.videos().list(part="snippet,contentDetails,statistics", id=video_id)
    response = request.execute()
    return response

# Update video details function
def update_video_details(youtube, video_id, new_title=None, new_description=None, new_tags=None):
    video_details = get_video_details(youtube, video_id)
    snippet = video_details["items"][0]["snippet"]

    if new_title:
        snippet["title"] = new_title
    if new_description:
        snippet["description"] = new_description
    if new_tags:
        snippet["tags"] = new_tags

    body = {"id": video_id, "snippet": snippet}
    request = youtube.videos().update(part="snippet", body=body)
    response = request.execute()
    return response

# Delete video function
def delete_video(youtube, video_id):
    request = youtube.videos().delete(id=video_id)
    response = request.execute()
    return response

# Streamlit App
def main():
    st.title("YouTube Video Manager")

    # Tabs for different operations
    tab1, tab2, tab3, tab4 = st.tabs(["Upload", "Read", "Update", "Delete"])

    with tab1:  # Upload Video
        st.header("Upload Video")
        video_file = st.file_uploader("Choose a video file", type=["mp4"])
        title = st.text_input("Title")
        description = st.text_area("Description")
        category_id = st.text_input("Category ID")
        tags = st.text_input("Tags (comma-separated)")

        if st.button("Upload"):
            if video_file and title and description and category_id and tags:
                youtube = authenticate()
                if youtube:
                    tags_list = [tag.strip() for tag in tags.split(",")]
                    response = upload_video(youtube, video_file, title, description, category_id, tags_list)
                    st.write(response)
            else:
                st.warning("Please fill in all fields.")

    with tab2:  # Get Video Details
        st.header("Get Video Details")
        video_id = st.text_input("Enter Video ID")

        if st.button("Get Details"):
            if video_id:
                youtube = authenticate()
                if youtube:
                    details = get_video_details(youtube, video_id)
                    st.write(details)

    with tab3:  # Update Video Details
        st.header("Update Video Details")
        video_id = st.text_input("Enter Video ID")
        new_title = st.text_input("New Title")
        new_description = st.text_area("New Description")
        new_tags = st.text_input("New Tags (comma-separated)")

        if st.button("Update"):
            if video_id:
                youtube = authenticate()
                if youtube:
                    tags_list = [tag.strip() for tag in new_tags.split(",")] if new_tags else None
                    response = update_video_details(youtube, video_id, new_title, new_description, tags_list)
                    st.write(response)

    with tab4:  # Delete Video
        st.header("Delete Video")
        video_id = st.text_input("Enter Video ID")

        if st.button("Delete"):
            if video_id:
                youtube = authenticate()
                if youtube:
                    response = delete_video(youtube, video_id)
                    st.write(response)

if __name__ == "__main__":
    main()

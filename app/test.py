
from google.oauth2 import service_account
from googleapiclient.discovery import build

scope = ["https://www.googleapis.com/auth/drive"]
service_account_json_key = "app/sa-google-drive-credentials.json"
credentials = service_account.Credentials.from_service_account_file(
    filename=service_account_json_key, scopes=scope
)
service = build("drive", "v3", credentials=credentials)

results = (
    service.files()
    .list(
        fields="files(id, name, mimeType, size, modifiedTime, trashed)",
        q='name contains ""',
    )
    .execute()
)
results_list = results.get("files", [])
# ids = [item['id'] for item in results_list if item['mimeType'] != 'application/vnd.google-apps.folder']
print(results_list)
# print(ids)
# for id in ids:
#     try:
#         service.files().update(fileId=id, body={'trashed': True}).execute()
#     except HttpError as err:
#         print('Couldnt do it for id:', id)

# results = service.files().list(fields="files(id, name, mimeType, size, modifiedTime)", q='name contains ""').execute()
# results_list = results.get("files", [])
# print(results_list)

# file_metadata = {"name": 'flats', 'parents': '<folder-id>'"mimeType": "text/csv"}
# media = MediaFileUpload('data/flats.csv', mimetype="text/csv", resumable=True)
# file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()

# request_file = service.files().get_media(fileId="1TZYDIl0kS2_eCgJnTUbUWyQN_BET8Mde")
# file = io.BytesIO()
# downloader = MediaIoBaseDownload(file, request_file)
# done = False
# while done is False:
#     status, done = downloader.next_chunk()
#     print(F'Download {int(status.progress() * 100)}.')
# file_retrieved = file.getvalue()
# with open(f"data/downloaded_file.csv", 'wb') as f:
#     f.write(file_retrieved)

import os
import tempfile
import requests
from moviepy.editor import VideoFileClip, concatenate_videoclips
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

class MergeVideos:
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    SERVICE_ACCOUNT_FILE = '/content/drive/My Drive/SD-Data/comfyui-n8n-aici01-7679b55c962b.json'
    DRIVE_FOLDER_ID = '1fZyeDT_eW6ozYXhqi_qLVy-Xnu5JD67a'

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_urls": ("STRING", {"tooltip": "Danh sách video URLs, mỗi URL một dòng hoặc cách nhau bằng dấu ','."})
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("output_video_url",)
    FUNCTION = "merge_and_upload_videos"
    CATEGORY = "video/audio"

    def __init__(self):
        self.drive_service = None
        self._initialize_drive_service()

    def _initialize_drive_service(self):
        try:
            credentials = service_account.Credentials.from_service_account_file(
                self.SERVICE_ACCOUNT_FILE, scopes=self.SCOPES)
            self.drive_service = build('drive', 'v3', credentials=credentials)
        except Exception as e:
            print(f"Error initializing Drive service: {str(e)}")
            raise RuntimeError(f"Failed to initialize Drive service: {str(e)}")

    def _upload_to_drive(self, file_path):
        try:
            file_metadata = {
                'name': os.path.basename(file_path),
                'parents': [self.DRIVE_FOLDER_ID]
            }
            media = MediaFileUpload(file_path, resumable=True)
            file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()

            self.drive_service.permissions().create(
                fileId=file.get('id'),
                body={'type': 'anyone', 'role': 'reader'},
                fields='id'
            ).execute()

            file_id = file.get('id')
            return f"https://drive.google.com/uc?id={file_id}"

        except Exception as e:
            raise RuntimeError(f"Failed to upload to Drive: {str(e)}")

    def merge_and_upload_videos(self, video_urls):
        """
        Ghép tất cả video từ danh sách video URLs và upload lên Google Drive.
        """
        temp_output_path = None  # Khởi tạo biến temp_output_path để tránh lỗi UnboundLocalError
        video_clips = []

        try:
            # Phân tách video_urls từ chuỗi
            urls = [url.strip() for url in video_urls.split(',')]
            
            # Tải từng video về và thêm vào danh sách video_clips
            for url in urls:
                response = requests.get(url)
                if response.status_code == 200:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video_file:
                        temp_video_file.write(response.content)
                        temp_video_path = temp_video_file.name
                        video_clips.append(VideoFileClip(temp_video_path))
                else:
                    print(f"Failed to download video from URL: {url}")

            # Ghép các video lại với nhau
            final_video = concatenate_videoclips(video_clips)

            # Tạo file tạm để lưu video đầu ra
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_output:
                temp_output_path = temp_output.name
                final_video.write_videofile(
                    temp_output_path,
                    codec='libx264',
                    audio_codec='aac',
                    remove_temp=True
                )

            # Tải lên Google Drive
            output_video_url = self._upload_to_drive(temp_output_path)
            return (output_video_url,)

        except Exception as e:
            raise RuntimeError(f"Failed to merge videos and upload: {str(e)}")

        finally:
            # Đóng tất cả video clips và xóa file tạm
            for clip in video_clips:
                clip.close()
            if temp_output_path and os.path.exists(temp_output_path):
                os.unlink(temp_output_path)

# A dictionary that contains all nodes you want to export with their names
NODE_CLASS_MAPPINGS = {
    "MergeVideos": MergeVideos
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "MergeVideos": "Merge Videos and Upload"
}

import requests
import subprocess
import os

class LoadVideoFromURLs:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "urls": ("STRING", {"multiline": True, "tooltip": "Danh sách các URL video, mỗi URL trên một dòng."}),
            }
        }

    RETURN_TYPES = ("STRING",)  # Trả về danh sách đường dẫn video đã tải
    RETURN_NAMES = ("video_files",)
    FUNCTION = "load_videos"

    def load_videos(self, urls):
        video_files = []
        for i, url in enumerate(urls.splitlines()):
            response = requests.get(url)
            video_file_path = f"video_{i}.mp4"
            with open(video_file_path, 'wb') as f:
                f.write(response.content)
            video_files.append(video_file_path)
        return (video_files,)

class MergeVideos:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_files": ("STRING", {"multiline": True, "tooltip": "Danh sách đường dẫn video để ghép, mỗi video trên một dòng."}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("merged_video",)
    FUNCTION = "merge_videos"

    def merge_videos(self, video_files):
        video_files_list = video_files.splitlines()
        concat_file = "videos_to_concat.txt"

        with open(concat_file, "w") as f:
            for video in video_files_list:
                f.write(f"file '{video}'\n")

        output_file = "merged_output.mp4"
        subprocess.run([
            "ffmpeg", "-f", "concat", "-safe", "0", "-i", concat_file,
            "-c", "copy", output_file
        ])
        
        return (output_file,)

class UploadToDestination:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file_path": ("STRING", {"tooltip": "Đường dẫn đến video đã ghép."}),
                "destination_url": ("STRING", {"tooltip": "URL nơi video sẽ được upload."}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("upload_result",)
    FUNCTION = "upload_video"

    def upload_video(self, file_path, destination_url):
        with open(file_path, 'rb') as f:
            response = requests.post(destination_url, files={'file': f})
        
        if response.ok:
            return (response.json(),)
        else:
            raise ValueError("Failed to upload video.")

# A dictionary that contains all nodes you want to export with their names
NODE_CLASS_MAPPINGS = {
    "LoadVideoFromURLs": LoadVideoFromURLs,
    "MergeVideos": MergeVideos,
    "UploadToDestination": UploadToDestination
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "LoadVideoFromURLs": "Load Video from URLs",
    "MergeVideos": "Merge Videos",
    "UploadToDestination": "Upload to Destination"
}

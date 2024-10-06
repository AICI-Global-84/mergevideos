import requests
import subprocess
import os
import ffmpeg


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

    def download_video(url, output_dir):
    response = requests.get(url)
    video_path = os.path.join(output_dir, url.split("/")[-1])  # Lưu video với tên file gốc
    with open(video_path, 'wb') as file:
        file.write(response.content)
    return video_path

    def merge_videos(video_urls, output_file):
        # Tải các video xuống trước
        downloaded_videos = [download_video(url, '/path/to/download/directory') for url in video_urls]
        
        # Lưu danh sách video vào file txt để ffmpeg sử dụng
        with open('videos_to_concat.txt', 'w') as f:
            for video in downloaded_videos:
                f.write(f"file '{video}'\n")
        
        # Sử dụng ffmpeg để ghép video
        ffmpeg.input('videos_to_concat.txt', format='concat', safe=0).output(output_file).run()
    
    # Ví dụ sử dụng
    video_urls = [
        "https://example.com/video1.mp4",
        "https://example.com/video2.mp4"
    ]
    merge_videos(video_urls, 'output_video.mp4')

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

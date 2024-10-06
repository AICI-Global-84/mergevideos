from .MergeVideos import LoadVideoFromURLs, MergeVideos, UploadToDestination

NODE_CLASS_MAPPINGS = {
    "LoadVideoFromURLs": LoadVideoFromURLs,
    "MergeVideos": MergeVideos,
    "UploadToDestination": UploadToDestination
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LoadVideoFromURLs": "Load Video from URLs",
    "MergeVideos": "Merge Videos",
    "UploadToDestination": "Upload to Destination"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

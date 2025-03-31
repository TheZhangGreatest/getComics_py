from enum import Enum

class DownloadStatus(str, Enum):
    PENDING = 'pending'
    DOWNLOADING = 'downloading'
    SUCCESS = 'success'
    FAILED = 'failed'
    PAUSED = 'paused'
    DELETED = 'deleted'

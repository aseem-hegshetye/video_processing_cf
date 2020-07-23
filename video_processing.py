import subprocess
from google.cloud import storage
import os
import re

class VideoProcessing:
    """
    Process video to good codecs in CS
    """
    video_path_on_cs = 'video_lecture/{file_name}'
    bucket_name = os.environ['bucket']

    def __init__(self, source_video_name_with_path_cs,
                 local=None):
        """
        :param source_video_name_with_path_cs: video_lecture/1.webm
            its entire video path on cloud storage
        :param local: if local=1 means running locally, use sv_account_key from
            settings. if local=None means running on CF,
            no need to specify sv_account_key.
        """
        self.video_name = source_video_name_with_path_cs.split('/')[-1]
        self.video_pk = self.video_name.split('.')[0]

        # cloud storage (source and processed) video names with entire path
        self.source_video_name_with_path_cs = source_video_name_with_path_cs
        self.processed_video_name_with_path_cs = self.get_processed_video_name_with_path_for_cs(
            source_video_name_with_path_cs
        )

        print(f'video_pk={self.video_pk}')
        self.local = local
        self.raw_video_name_with_path_local = '/tmp/{}'.format(
            self.video_name
        )
        self.processed_video_name_with_path_local = '/tmp/{}_processed.mp4'.format(
            self.video_pk
        )

        shell_cmd = 'ffmpeg -i {input_video} -vcodec libx264 -acodec aac {output_video}'
        self.video_process_shell_cmd = shell_cmd.format(
            input_video=self.raw_video_name_with_path_local,
            output_video=self.processed_video_name_with_path_local
        )

        # if running on CF. default service account will be used
        if self.local is None:
            storage_client = storage.Client()

        # running locally on my laptop so need a service account key file
        # to make calls to Cloud storage
        else:
            from django.conf import settings
            storage_client = storage.Client.from_service_account_json(
                settings.SERVICE_ACCOUNT_KEY_NAME
            )

        self.bucket = storage_client.bucket(self.bucket_name)

    def process_video(self):
        """
        delete local videos incase anything from previous run exists.
        download video (1.webm) from CS, store it locally
        convert video to desired codec (1_processed.mp4)
        upload new video to CS
        delete local videos.
        delete old video file (1.webm) from CS.
        """
        self.delete_local_videos()
        self.download_raw_video_from_cs()
        self.convert_video_codecs()
        self.upload_processed_video_to_cs()
        self.delete_local_videos()
        self.delete_raw_video_from_cs()

    def delete_raw_video_from_cs(self):
        """
        delete raw video from CS
        """
        print('delete_raw_video_from_cs')
        blob = self.bucket.blob(self.source_video_name_with_path_cs)
        blob.delete()

    def delete_local_videos(self):
        """
        delete local copies of video from CF /tmp/ folder
        """
        print('delete_local_videos')
        if os.path.exists(self.raw_video_name_with_path_local):
            print(f'raw_video_name_with_path_local={self.raw_video_name_with_path_local}')
            os.remove(self.raw_video_name_with_path_local)
        if os.path.exists(self.processed_video_name_with_path_local):
            os.remove(self.processed_video_name_with_path_local)

    def upload_processed_video_to_cs(self):
        """
        upload processed video to CS with name
        pk_processed.mp4
        """
        print('upload_processed_video_to_cs')
        blob = self.bucket.blob(self.processed_video_name_with_path_cs)
        blob.upload_from_filename(self.processed_video_name_with_path_local)

    def convert_video_codecs(self):
        """
        convert video into proper codec and save processed file
        locally
        """
        output = subprocess.check_output(self.video_process_shell_cmd, shell=True)
        print(f'video processed sucess. output={output}')

    def download_raw_video_from_cs(self):
        """
        download blob from CS to local dir - /tmp/{video_name}
        """
        print('download_raw_video_from_cs')
        blob = self.bucket.blob(self.source_video_name_with_path_cs)
        blob.download_to_filename(
            self.raw_video_name_with_path_local
        )

    def get_processed_video_name_with_path_for_cs(self, source_video):
        """
        :param source_video: 'video_lecture/1.webm'
        :return: complete cloud storage (CS) path for processed video
            using cs video path for source video.
            'video_lecture/1_processed.mp4'
        """
        print('get_processed_video_name_with_path_for_cs')
        path = '/'.join(source_video.split('/')[:-1])
        return '{}/{}_processed.mp4'.format(
            path, self.video_pk
        )


Video processing on GCP cloud function using ffmpeg

I have a website where users upload videos which are stored to cloud storage. These videos could be in any format, hence they are sometimes not compatible with certain devices. Eg: webm videos uploaded from a laptop are not compatible with mobile browsers.
We will create a Cloud Function that will process a video as soon as its uploaded to cloud storage. 

https://www.encoding.com/html5-video-codec/ this article shows all audio video codecs and their compatibility with different devices. We will use MP4 video code and AAC audio codec.

Create a Cloud Function on GCP and associate it with the bucket that receives user uploaded videos. Make it trigger on event type = Finalize/Create . 
Every Cloud Function comes with ffmpeg installed in it. Following is the workflow used in video_processing.py to process a video from CS using ffmpeg:
* Download video (1.webm) from CS (cloud storage) to tmp folder on CF (cloud function). tmp folder is the only folder that gives us write permissions on CF.
* process the video using ffmpeg and save results (1_processed.mp4) in tmp folder.
* upload processed video to CS.
* delete all videos from local tmp folder on CF.
* delete original raw video (1.webm) from CS.

To use video_processing.py file in CF:
```
video_obj = VideoProcessing(video_name)
video_obj.process_video()
```

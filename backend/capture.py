import os
import cv2
import time

file_path = os.path.dirname(os.path.realpath(__file__))
video_path = file_path + "/capture/testvid.MOV"


def extract_frame_from_video(video_file_path, frames = None, capture_rate = 1):
    print(f"Extracting {video_file_path} at 1 frame per second. This might take a bit...")
    vidcap = cv2.VideoCapture(video_file_path)
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    print(fps)
    output_file_prefix = os.path.basename(video_file_path).replace('.', '_')
    frame_count = 0.0
    count = 0
    vidnum = 0
    added_folder = False
    if (not os.path.exists(file_path + f"/content/vid{vidnum}")):
        os.mkdir(file_path + f"/content/vid{vidnum}")
    print(f"Starting extraction of video: {vidnum}")
    while vidcap.isOpened():
        success, frame = vidcap.read()
        if not success: # End of video
            break
        #print(vidnum, " ", (frame_count), " ", abs((count / (fps / capture_rate)) - (frame_count)))
        if (abs((count / (fps / capture_rate)) - (frame_count)) <= .1): # Extract a frame every second
            added_folder = False
            min = frame_count // 60
            sec = frame_count % 60
            subsec = (frame_count % 1) * 100
            time_string = f"{int(min):02d}:{int(sec):02d}:{int(subsec):02d}"
            image_name = f"{output_file_prefix}_frame{time_string}.jpg"
            output_filename = os.path.join(file_path + f"/content/vid{vidnum}", image_name)
            cv2.imwrite(output_filename, frame)
            frame_count += 1 / capture_rate
        if ((frame_count) != 0 and (not added_folder) and (frame_count) % int(frames / capture_rate) == 0):
            print(f"Finished video: {vidnum}")
            added_folder = True
            vidnum += 1
            print(f"Starting extraction of video: {vidnum}")
            if (not os.path.exists(file_path + f"/content/vid{vidnum}")):
                os.mkdir(file_path + f"/content/vid{vidnum}")
        """
        if (frames and int(frame_count) >= int(frames / capture_rate)):
            break
        """
        count += 1
    vidcap.release() # Release the capture object\n",
    print(f"Completed video frame extraction!\n\nExtracted: {frame_count / capture_rate} frames")

extract_frame_from_video(video_path, 120, 2)
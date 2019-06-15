#!/usr/bin/env python3

''' Make the podcast. '''

import argparse
import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

__author__ = 'Sean Mooney'
__email__ = 'mooneyse@tcd.ie'
__date__ = '09 June 2019'

# add a function to download a video from YouTube, strip the audio, and trim it
# to a give start and stop time

# have the OL image hosted on GitHub and download it from there each time

# make a GitHub Pages page for OL using Flask or Jekyll

def make_video(audio, image='ol.png'):
    ''' Make a video with the audio and a still image. '''

    cmd = 'ffmpeg -loop 1 -i {image} -i {audio} -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -shortest video.mp4'.format(audio=audio, image=image)


def youtube_upload(video):
    ''' Upload the video to YouTube. '''

    # https://developers.google.com/youtube/v3/guides/uploading_a_video

    pass


def drive_upload(video):
    ''' Upload the video to Google Drive. '''

    # https://pythonhosted.org/PyDrive

    # set up api
    g_login = GoogleAuth()
    g_login.LocalWebserverAuth()
    drive = GoogleDrive(g_login)

    # create folder

    # upload file
    with open(video, 'r') as file:
        pass

    print('{} has been uploaded to Google Drive'.format(video))


def tidy_up(audio, image, video):
    ''' Upload the video to Google Drive. '''

    pass


def main():
    ''' Make the podcast. '''

    formatter_class = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=formatter_class)

    parser.add_argument('audio', type=str, help='Audio file.')

    args = parser.parse_args()
    audio = args.audio

    make_video(audio)
    youtube_upload(video)
    drive_upload(video)
    tidy_up(audio, image, video)


if __name__ == '__main__':
    main()

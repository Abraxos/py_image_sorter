# Python Image Sorter

An image sorting program written in Python using PyGTK2

## Requirements

This program requires that you have PyGTK2 installed. Aside from that it uses standard Python libraries. This program has not been tested on Windows. I have no idea how to make it work there so don't ask, although feel free to contribute to the project if you want to make it work, but not at the cost of Linux support.

## Usage

### Launching the Program

Simply execute this from the commandline:

```
$ python image_sorter.py
```

You will then be prompted for a directory to scan for images. If there are no images in the directory the program will simply close.

### User's Guide

This program was designed to make it extremely easy to sort a directory of images into more organized folders. On launch, as described above, the program prompts you for a directory and scans it for image files. The Python Image Sorter works by having the user press keys for each image which determine which directory the image gets sorted into. You can go back to change your choices because each button press marks the image for moving/copying and only executes the changes when you press `Enter` to commit. It has the following features:

+ With an image open, pressing a letter key on your keyboard will mark the picture to be moved to the directory associated with the letter.
  + If this is the first time you've pressed that button during this run of the program, you will be prompted for a directory to be associated with the letter key.
+ You can press `Shift + <Letter>` to mark the file to be copied to the directory associated with the letter key.
  + Marking an image for copying will not move the program on to the next image (whereas marking an image to be moved will)
+ You can move forward and backwards in the list of images using the left/right arrow keys.
  + You can choose to move images to different directories than before.
  + You can add new destinations for the file to be copied to.
+ You can mark images for deletion by pressing the delete key, pressing it a second time on the same image will mark it to not be deleted.
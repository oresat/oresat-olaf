# import the opencv library
import cv2
import os

#define file path for saved image
#file_path = r'C:\Users\vevg\Documents\ECE508\testcode\ImageTest.jpeg'

#set dir to current directory
dir = os.path.dirname(__file__)

filename = os.path.join(dir, 'image1.jpeg')

print(filename)

# define a video capture object
vid = cv2.VideoCapture(0)

# Capture the image
result, image = vid.read()


#show the image
cv2.imshow("Image", image)


# saving image in that directory
ret = cv2.imwrite(filename, image)

print(ret)
  
# close window on keyboard interrupt
cv2.waitKey(0)
cv2.destroyAllWindows()
  

# After the loop release the cap object
vid.release()
# Destroy all the windows
cv2.destroyAllWindows()

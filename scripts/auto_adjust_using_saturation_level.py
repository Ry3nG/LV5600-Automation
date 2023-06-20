from time import sleep
import cv2
import numpy as np
from .capture_and_send_bmp import capture_and_send_bmp
from .recall_preset import recall_preset
import logging
from Constants import Constants

x1 = 57
x2 = 750
y1 = 510
y2 = 1320
satCount = 5 # saturated pixel count
image_dir = Constants.LOCAL_FILE_PATH_BMP
buffer_dir = Constants.LOCAL_BUFFER_PATH
offset = 25

def GetWaveformTopProfile(img):
	h, w = img.shape[:2]
	x = list(range(0,w))

	arrImg = np.array([])
	for i in range(w):
		y = img[:,i,1]
		arrImg = np.append(arrImg, y.argmax())

	arrImg = np.vstack((x, arrImg))
	arrImgUpsideDown = h-arrImg[1]
	arrImgUpsideDown = np.vstack((x, arrImgUpsideDown))
	
	return(arrImg, arrImgUpsideDown)

def GetSaturatedValue(arr, offset):
	center = int(arr.shape[1]/2)
	upper  = int(center + offset)
	lower  = int(center - offset)

	arrCropped = arr[:, lower:upper]
	arrDiffneighbourPx = np.diff(arrCropped[1])     # difference diff[i] = a[i+1]-a[i]
	std = arrDiffneighbourPx.std()
	
	if std == 0:
		max = arrCropped[1].max()
	else:
		max = 0
	
	return max

def IsSaturated(arr, saturatedValue, offset, saturatedPxCount):
    center = int(arr.shape[1]/2)
    upper  = int(center + offset)
    lower  = int(center - offset)
    arrCropped = arr[:, lower:upper]
    countSat = np.count_nonzero(arrCropped[1] == saturatedValue)
    print("countSat: ", countSat)
    if countSat >= saturatedPxCount:
        return True
    else:
        return False

async def auto_adjust_using_saturation_level(telnet_client, ftp_client,debugConsoleController, current_level):
    
    # recall preset 6
    try:
        await recall_preset(telnet_client, "6")
        logging.info("Recalled preset: 6")
    except Exception as e:
        logging.error(f"Failed to change preset: {e}")
    sleep(1)
    try:
        await capture_and_send_bmp(telnet_client, ftp_client)
        logging.info("Captured and sent bmp.")
    except Exception as e:
        logging.error(f"Failed to capture and send bmp: {e}")

    img = cv2.imread(image_dir)
    frameCrop = img[x1:x2,y1:y2]

    _, arr02 = GetWaveformTopProfile(frameCrop)
    satValue = GetSaturatedValue(arr02, offset)
    if satValue > 0:
        print('Saturated value: {}'.format(satValue))
    
    debugConsoleController.tune_to_target_level(5,current_level)
    current_level = 5


    flag = False
    while(flag != True):
        print("Turning up the light ... ")
        debugConsoleController.tune_up_light()
        try:
            await capture_and_send_bmp(telnet_client, ftp_client)
            logging.info("Captured and sent bmp.")
        except Exception as e:
            logging.error(f"Failed to capture and send bmp: {e}")

        img = cv2.imread(image_dir)
        frameCrop = img[x1:x2,y1:y2]

        _, arr02 = GetWaveformTopProfile(frameCrop)
        satValue_cur = GetSaturatedValue(arr02, offset)
        print('Saturated value currently: {}'.format(satValue_cur))

        if IsSaturated(arr02, satValue, offset, satCount):
            flag = True
            print("Saturated")
	
	    


import cv2
def variance_of_laplacian(image):
	return cv2.Laplacian(image, cv2.CV_64F).var()
 
def blurDetect(path,s_frame,duration_perclip):
	print('detecting blur..')
	frm = s_frame
	pfm = 0
	if(duration_perclip!=0):
		e_frame = int(s_frame+duration_perclip)

	global cap
	cap = cv2.VideoCapture(path)
	cap.set(1,s_frame)
	while(cap.isOpened()):
		if(frm<s_frame):
			cap.grab()
		else:
			ret, frame = cap.read()
			gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
			fm = variance_of_laplacian(gray)
			if (pfm - fm > 500):
				print('detect blur at frame : ',frm)
				return 0
			#pfm = fm
			if(frm==e_frame):
				print('no blur detected')
				return 1
			pfm = fm
		frm +=1
	cap.release()
	#cv2.destoryAllWindows()



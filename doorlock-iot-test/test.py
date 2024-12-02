import cv2
import requests
from datetime import datetime
import time

# Backend API endpoint
API_URL = 'http://192.168.222.200:8000/api/detect_qr_code/'

# Initialize webcam
cap = cv2.VideoCapture(0)
qr_code_detector = cv2.QRCodeDetector()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture frame")
        break

    # Detect QR code
    qr_data, bbox, _ = qr_code_detector.detectAndDecode(frame)

    # Draw bounding box around detected QR code (if any)
    if bbox is not None:
        bbox = bbox.astype(int)  # Convert coordinates to integers

        # Check if bbox has 4 points (a quadrilateral)
        if len(bbox) == 4:
            # Draw rectangle using the first and third corners of the bbox
            pt1 = tuple(bbox[0][0])  # Top-left corner
            pt2 = tuple(bbox[2][0])  # Bottom-right corner
            cv2.rectangle(frame, pt1, pt2, (0, 255, 0), 3)  # Green rectangle

    if qr_data:
        print(f"QR Code detected: {qr_data}")

        # Save screenshot
        screenshot_path = "screenshot.png"
        cv2.imwrite(screenshot_path, frame)
        print("Screenshot saved!")

        # Prepare data for the backend
        payload = {
            'qr_code': qr_data,
            'timestamp': datetime.now().isoformat(),  
        }

        # Open the screenshot file to send
        with open(screenshot_path, 'rb') as screenshot_file:
            files = {
                'screenshot': screenshot_file,  # Attach the screenshot
            }

            # Send the data to the backend
            try:
                response = requests.post(API_URL, data=payload, files=files)
                if response.status_code == 200:
                    print("Data sent successfully:", response.json())
                    time.sleep(8)
                else:
                    print("Failed to send data:", response.json())
            except Exception as e:
                print(f"Error sending data to server: {e}")

    # Add text on the screen
    cv2.putText(frame, "SISTEM IOT DOOR LOCK AEROBO", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

    # Display the frame
    cv2.imshow("QR Code Scanner", frame)

    # Exit on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
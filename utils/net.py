import cv2


def image_to_bytes(image):
    success, encoded_image = cv2.imencode('.png', cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    assert success, 'Can\'t encode image.'
    return encoded_image.tobytes()

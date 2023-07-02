import win32gui
import win32ui
import win32con
import numpy as np
import time


def grab(left, top, width, height):
    # Get desktop
    hdesktop = win32gui.GetDesktopWindow()

    # Create device description table
    desktop_dc = win32gui.GetWindowDC(hdesktop)
    img_dc = win32ui.CreateDCFromHandle(desktop_dc)
    # Create a memory device description table
    mem_dc = img_dc.CreateCompatibleDC()
    # Create bitmap object screenshot = BMP
    screenshot = win32ui.CreateBitmap()
    screenshot.CreateCompatibleBitmap(img_dc, width, height)
    mem_dc.SelectObject(screenshot)
    # Screenshot to memory device description table
    mem_dc.BitBlt((0, 0), (width, height), img_dc, (0, 0), win32con.SRCCOPY)

    # Obtain image from bitmap
    signed_ints_array = screenshot.GetBitmapBits(True)
    img = np.frombuffer(signed_ints_array, dtype='uint8')
    img.shape = (height, width, 4)
    img = img[:, :, :3]

    # Memory release
    mem_dc.DeleteDC()
    win32gui.DeleteObject(screenshot.GetHandle())

    return img


start = time.time()
grab(0, 0, 1920, 1080)
end = time.time()
print(f'fps: {1/ (end - start)}')


import numpy as np
import cv2
from mss import mss
import d3dshot
import time
from multiprocessing import Process, Queue, Value

width, height = 2560, 1440
fps = 24


def grab_worker(q_in, flag, flag1):
    # Init grabber
    sct = mss()
    bbox = (0, 0, width, height)
    count = 0
    while True:
        if flag.value != -1:
            if flag1.value <= fps:
                # Obtain frame start time
                start = time.time()
                count += 1
                # Grab frame, put into image_in
                frame = sct.grab(bbox)
                # Obtain frame end time
                end = time.time()
                # Obtain time difference
                wait_time = ((1/fps) - (end - start)) * 0.98
                # Skip wait if fps is behind
                if wait_time > 0:
                    time.sleep(wait_time)
                flag1.value += 1
                q_in.put(frame)
        else:
            print("Grab worker stopping...")
            break


def image_worker(q_in, q_out, flag, flag1, flag2):
    while True:
        if flag.value != -1:
            if flag1.value >= 1 and flag2.value <= fps:
                frame = q_in.get()
                flag1.value -= 1
                frame = np.asarray(frame)
                frame = frame[:, :, :3]
                q_out.put(frame)
                flag2.value += 1
        elif flag.value == -1 and flag1.value == 0 and flag2.value == 0:
            print("image worker stopping...")
            break
        elif flag.value == -1 and flag1.value > 0:
            frame = q_in.get()
            flag1.value -= 1
            frame = np.array(frame)
            frame = frame[:, :, :3]
            q_out.put(frame)
            flag2.value += 1


def write_worker(q_out, flag, flag1, flag2, filename):
    # Resolution
    resolution = (width, height)
    # Codec for video writer
    codec = cv2.VideoWriter_fourcc(*"XVID")
    # Init video writer object
    output = cv2.VideoWriter(filename, codec, fps, resolution)
    while True:
        if flag.value != -1:
            if flag2.value >= 1:
                frame = q_out.get()
                output.write(frame)
                flag2.value -= 1
        elif flag.value == -1 and flag1.value ==0 and flag2.value == 0:
            print("write worker stopping...")
            output.release()
            break
        elif flag.value == -1 and (flag1.value > 0 or flag2.value > 0):
            frame = q_out.get()
            output.write(frame)
            flag2.value -= 1


if __name__ == '__main__':
    f_name = input("Enter filename: ") + ".avi"

    # Init multi-processing
    f_1 = Value('i', 0)
    f_2 = Value('i', 0)
    status = Value('i', 0)
    image_in = Queue()
    image_out = Queue()

    cv2.namedWindow("Stop Window", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Stop Window", 100, 50)

    g_worker = Process(target=grab_worker, args=(image_in, status, f_1,))
    i_worker = Process(target=image_worker, args=(image_in, image_out, status, f_1, f_2))
    w_worker = Process(target=write_worker, args=(image_out, status, f_1, f_2, f_name))

    g_worker.start()
    i_worker.start()
    w_worker.start()

    while True:
        if cv2.waitKey(1) == ord("q"):
            status.value = -1
            cv2.destroyAllWindows()
            break

    g_worker.join()
    i_worker.join()
    w_worker.join()
    print("Process cleaned")

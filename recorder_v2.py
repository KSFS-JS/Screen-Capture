import cv2
import d3dshot
import time
from multiprocessing import Process, Queue, Value

width, height = 2560, 1440
resolution = (1600, 900)
fps = 24


def grab_worker(q_in, flag, flag1):
    # Init grabber
    grabber = d3dshot.create(capture_output="numpy")
    bbox = (0, 0, width, height)
    while True:
        if flag.value != -1:
            # Grab frame, put into image_in
            start = time.time()

            # Get frame
            frame = grabber.screenshot(region=bbox)
            # Send to processor
            q_in.put(frame)
            flag1.value += 1

            end = time.time()
            # compensate frames
            wait_time = ((1 / fps) - (end - start)) * 0.95
            # Skip wait if fps is behind
            if wait_time > 0:
                time.sleep(wait_time)
        else:
            print("Grab worker stopping...")
            break


def image_worker(q_in, q_out, flag, flag1, flag2):
    while True:
        if flag.value != -1:
            if flag1.value >= 1:
                frame = q_in.get()
                flag1.value -= 1

                # Reduce resolution for space saving
                frame = cv2.resize(frame, resolution)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                q_out.put(frame)
                flag2.value += 1
        elif flag.value == -1 and flag1.value == 0 and flag2.value == 0:
            print("image worker stopping...")
            break
        elif flag.value == -1 and flag1.value > 0:
            frame = q_in.get()
            flag1.value -= 1
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            q_out.put(frame)
            flag2.value += 1


def write_worker(q_out, flag, flag1, flag2, filename):
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
        elif flag.value == -1 and flag1.value == 0 and flag2.value == 0:
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

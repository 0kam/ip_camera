import requests
from time import sleep
import cv2
import av
import sounddevice
import numpy

class JennovCam():
    def __init__(self, host, user, passwd):
        self.__url = "http://{}:{}@{}/web/cgi-bin/hi3510/".format(user, passwd, host)
        self.__ptzctrl("stop", 63)
        self.__url_stream = "rtsp://{}:{}@{}/1".format(user, passwd, host)
    
    # PTZ
    def ptz(self, cmd, speed=63, sec=1.0):
        """
        パンチルト

        Parameters
        ----------
        cmd : str
            "right", "left", "up", "down" のいずれか
        speed : int default 63
            モータの速さ。1~63。
        sec : float default 1.0
            動かす時間（秒）。
        """
        self.__ptzctrl(cmd, speed)
        sleep(sec)
        self.__ptzctrl("stop", 63)

    def __ptzctrl(self, cmd, speed):
        requests.get("{}/ptzctrl.cgi?-step=0&-act={}&-speed={}".format(self.__url, cmd, speed))
    
    def set_preset(self, number, status=1):
        """
        現在のカメラの向きでプリセットを設定する

        Parameters
        ----------
        number : int
            プリセット番号。0~66（Jennov T-Series）。
        status : int default 1
            0 to save, 1 to clear
        """
        requests.get("{}/preset.cgi?-act=set&-status={}&-number={}".format(self.__url, status, number))
    
    def goto_preset(self, number):
        """
        プリセットに移動する

        Parameters
        ----------
        number : int
            プリセット番号。0~66（Jennov T-Series）。
        """
        requests.get("{}/preset.cgi?-act=goto&-number={}".format(self.__url, number))
    
    # Image Capturing
    def snap_shot(self):
        """
        スナップショットを撮る

        Returns
        -------
        image : np.array
            
        """
        stream = cv2.VideoCapture(self.__url_stream)
        r, f = stream.read()
        if r:
            stream.release()
            return f
        else: 
            raise ValueError("Failed to read the stream")
    
    def view_stream(self):
        """
        ライブビュー。q で停止。
        """
        stream = cv2.VideoCapture(self.__url_stream)
        while True:
            _, f = stream.read()
            cv2.imshow("IPCamera, press 'q' to stop", f)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        cv2.destroyAllWindows()
        stream.release()
    
    def set_infrared(self, infrared="close"):
        """
        赤外線カットフィルターの操作。

        Parameters
        ----------
        infrared str default "close"
           "open" to get infrared image, "close" to get normal RGB image.
        """
        requests.get("{}/param.cgi?cmd=setinfrared&-infraredstat={}".format(self.__url, infrared))
    
    def stream_sound(self):
        container = av.open(self.__url_stream)
        stream = sounddevice.OutputStream(samplerate=container.streams.audio[0].sample_rate)
        for frame in container.decode(video=0,audio=1):
            if type(frame) is av.video.frame.VideoFrame:
                img = frame.to_ndarray(format='bgr24')
                cv2.imshow("Test", img)
                key=cv2.waitKey(1)
            elif  type(frame) is av.audio.frame.AudioFrame:
                audio=frame.to_ndarray(format='s16')
                audio = numpy.rot90(audio,-1).copy(order="C")
                stream.write(audio)
                if stream.stopped:
                    stream.start()
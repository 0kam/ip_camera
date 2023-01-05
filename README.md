# Jennov Camera
Jennov のIPカメラをHTTPから操作するためのPythonモジュール。
Jennov T-Serieseでテスト済み
安い中華IPカメラは多くがFDT社製のAPIを流用している。
添付のPDFは以下から取得したFDT社製IPカメラのCGIガイドであり、
他のカメラでもこのマニュアルにしたがってAPIを叩けば動作する可能性がある。  
https://s3.amazonaws.com/fdt-files/FDT+IP+Camera+CGI+%26+RTSP+User+Guide+v1.0.2.pdf  
このスクリプトでは、Jennov T-Serieseで操作できる以下の内容について実装している。
- PTZ操作（T-SerieseはZoomができないのでZoomは未実装、簡単にできるはず）
- 赤外線カットフィルタのオンオフ
- 画像の取得
- 動画のストリーミング再生

## Example:
```python
from jennov_camera import JennovCam

cam = JennovCam("192.168.1.88", "admin", "admin")

cam.ptz("left", 63, 0.5)
cam.ptz("right", 63, 0.5)
cam.ptz("up", 50, 1)
cam.ptz("down", 50, 1)

cam.set_preset(1)
cam.ptz("left", 63, 0.5)
cam.ptz("down", 63, 0.5)
cam.goto_preset(1)

import cv2
cam.set_infrared("close")
image = cam.snap_shot()
cv2.imwrite("rgb.png", image)

cam.set_infrared("open")
image = cam.snap_shot()
cv2.imwrite("ir.png", image)

cam.view_stream()
```

## TODO
- 動かす -> sleep -> 止める だと同じ秒数でも動いた角度がばらつく（通信のオーバーヘッドとか？）のでより正確なPTZが必要
- cv2.VideoCapture()を画像を取得するたびに呼び出している（__init__()でself.stream = cv2.VideoCapture()とすると撮れなくなる）ため連写が遅い
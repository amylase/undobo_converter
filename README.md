# undobo_converter

## 概要

2つのノブの入力をマウスの動きに変換するアナログコントローラー（ボルテコン）の入力をキーボード入力に変換します。
コナミアミューズメント社製『コナステ版 SOUND VOLTEX』シリーズで利用することを意図しています。

[中華ボルテコン変換機](http://otogetool.g2.xrea.com/)と同等のソフトウェアです。


## 利用方法

`main.exe` を起動してください。Ctrl+F12 で変換をオン/オフできます。Ctrl+Cで終了します。


## 設定

### キーアサイン

`config.json` の `x_negative`, `x_positive`, `y_negative`, `y_positive` を変更してください。


## ビルド

```
pyinstaller --onefile main.py
```

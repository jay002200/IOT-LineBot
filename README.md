# IOT-LineBot

## 名稱
喔wow太智慧了吧宿舍

## 簡介
使用LineBot，讓房客與房東有個快速、方便回報問題的管道，結合MQTT，讓房客可以控制自己房間的電器，以及開啟大門。

## 功能
### 管理員：

* 用戶註冊列表：列出要註冊的房客列表。
* 房客回報問題列表：列出房客們回報的問題。
* 查詢房客：輸入房客的房號，調出房客的基本資料。

### 房客：

* 開門：輸入開門即可開啟宿舍大門。
* 房間資訊：查看目前房間室內溫度及濕度(尚未實裝)，以及台灣目前電力使用狀況。
* 開/關啟電燈(尚未實裝)：開/關自己房間的電燈。
* 開/關閉插座電源：開/關自己房間的插座電源。
* 故障回報：將故障或問題回報給房東，可附照片。

## 使用說明
### 指令查詢
```
help
```
### 註冊
* 加入帳號為好友後，傳送訊息"房客註冊"，會要求你輸入姓名、房號、電話和信箱，驗證碼會寄到信箱，輸入正確的驗證碼後需等管理員確認後，完成註冊。
* 註冊成功後，會發送信件通知。

<img src="https://github.com/jay002200/IOT-LineBot/blob/main/img/us1-1.jpg">
用戶端
<img align="left" src="https://github.com/jay002200/IOT-LineBot/blob/main/img/ad1-1.png"><img  src="https://github.com/jay002200/IOT-LineBot/blob/main/img/ad1.jpg">
管理員端
<img src="https://github.com/jay002200/IOT-LineBot/blob/main/img/us2.png">
用戶收到確認信

### 房間資訊
查看房間的溫度和濕度，以及台灣目前用電量。
* (資料來自https://www.taipower.com.tw/tc/page.aspx?mid=206)
<img src="https://github.com/jay002200/IOT-LineBot/blob/main/img/us3.jpg">

### 開啟/關閉電器
* 傳送指令，房客就可開/關自己房間的插座電源。
```
指令:開啟電器
```
<img src="https://github.com/jay002200/IOT-LineBot/blob/main/img/207088.gif">
```
指令:關閉電器
```
<img src="https://github.com/jay002200/IOT-LineBot/blob/main/img/207087.gif">
關閉電源

### 故障回報
* 房客回報故障需要維修或是問題給房東。
```
指令：r(空格)您要回報的問題
```
<img align="left" src="https://github.com/jay002200/IOT-LineBot/blob/main/img/us4.jpg"><img  src="https://github.com/jay002200/IOT-LineBot/blob/main/img/us5.jpg">

用戶端

<img align="left" src="https://github.com/jay002200/IOT-LineBot/blob/main/img/ad3.jpg"><img  src="https://github.com/jay002200/IOT-LineBot/blob/main/img/ade2.jpg">




管理員收到通知後，更改進度。




<img src="https://github.com/jay002200/IOT-LineBot/blob/main/img/us7.png">
用戶收到進度通知。






### 開門
* 傳送指令，房客就可開啟大門。
<img src="https://github.com/jay002200/IOT-LineBot/blob/main/img/x4cg4-drlt1.gif">


### 查詢房客(管理員)
* 查詢房客的基本資料。
```
指令：find(空格)房客的房號
```

![alt text](https://github.com/jay002200/IOT-LineBot/blob/main/img/ad2.jpg)

## 使用到的工具
### 軟體
* python
* flask
* mysql
* Line Bot-SDK
* Mosquitto
* Line
* ngrok
### 硬體
* Arduino ESP8266、ESP32
* 電腦
* 手機









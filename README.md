# Kindlereader (gae)

一个定时将Google reader发送至kindle的工具，运行于 Google App Engine, demo [http://reader.dogear.mobi](http://reader.dogear.mobi)

## 安装

* 修改 app.yaml 中 application id,
* 将 config.example.py 更名为 config.py 并配置其中内容
* 如果账单开启则将 queue.example.billing.yaml 更名为 queue.yaml 否则将 queue.example.yaml 更名为 queue.yaml
* 使用 Google App Engine Launcher 上传至服务器

## 许可

Kindlereader is Licensed under the MIT license: [http://www.opensource.org/licenses/mit-license.php](http://www.opensource.org/licenses/mit-license.php)
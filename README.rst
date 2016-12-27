与浏览器保持长连接的webscoket服务
================================

前端使用流程:
-------------

#. 建立webscoket连接

    .. code:: js

        var ws = new WebSocket("ws://<domain>/channel");


#. 设置channel_id, 如果channel_id未指定(null 或者 '')，则由服务器返回channel_id

    .. code:: js

        ws.onopen = function() {
            var msg = {
                channel_id: null
            };
            ws.send(JSON.stringify(msg));
        };

#. 处理服务器push过来的消息

    .. code:: js

        ws.onmessage = function (evt) {
            var data = JSON.parse(evt.data);
            console.log("response data is: " + JSON.stringify(data));
        };


push数据流程：
-------------

#. 例如对channel_id: 123123 推送一个随机数

    .. code:: python

        # -*- coding: utf-8 -*-
        import random
        import requests

        url = 'http://localhost:9012/push'
        data = dict(
            channel_id='123123',
            data=dict(
                ran=random.randint(1, 10)
            )
        )
        r = requests.post(url, json=data)

        print(r.text)

#. 前端将收到如下数据

    .. code:: js

        {
            ran: 3
        }

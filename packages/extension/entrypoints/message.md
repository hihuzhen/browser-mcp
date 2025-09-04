## 消息机制概览

### 1\. 来自运行时的消息 (ServerMessageType)

| 类型 | 描述 |
| :--- | :--- |
| **`PING_WEBSOCKET`** | 返回 WebSocket 连接是否正在运行。 |
| **`GET_WEBSOCKET_STATUS`** | 返回 WebSocket 的当前状态。 |
| **`CONNECT`** | 将 `shouldConnect` 状态设置为 `true`，并尝试连接 WebSocket。 |
| **`DISCONNECT`** | 断开 WebSocket 连接，并将 `shouldConnect` 状态设置为 `false`。 |

-----

### 2\. WebSocket 消息机制

| 事件 | 描述 |
| :--- | :--- |
| **`onopen`** | 连接成功后，处理所有积压的消息。 |
| **`onclose`** | 连接关闭时，不进行任何消息处理。 |
| **`onerror`** | 发生错误时，向服务器发送一个错误消息，内容为 `{ type: WebSocketMessageType.ERROR, error: ERROR_MESSAGES.CONNECTION_FAILED }`。 |
| **`onmessage`** | 收到消息时，根据消息类型进行处理： |

#### `onmessage` 消息处理详情

1.  **处理错误消息格式：**
    如果消息格式不正确，向发送方返回一个错误消息：

    ```json
    {
      "type": "WebSocketMessageType.ERROR",
      "responseToRequestId": "messageObj?.requestId",
      "error": "ERROR_MESSAGES.INVALID_MESSAGE"
    }
    ```

2.  **处理 Ping 消息：**
    如果收到 Ping 消息，向发送方返回一个 Pong 消息以确认连接状态：

    ```json
    {
      "type": "WebSocketMessageType.PONG",
      "responseToRequestId": "message.requestId"
    }
    ```

3.  **处理 Pong 消息：**
    收到 Pong 消息时，不进行任何消息处理。

4.  **处理 `calltool` 消息：**

    * **正常处理 (Success)：**
      如果工具调用成功，返回一个成功的响应：
      ```json
      {
        "type": "WebSocketMessageType.CALL_TOOL_RESPONSE",
        "responseToRequestId": "requestId",
        "payload": {
          "status": "success",
          "message": "SUCCESS_MESSAGES.TOOL_EXECUTED",
          "data": "result"
        }
      }
      ```
    * **异常处理 (Error)：**
      如果工具调用失败，返回一个包含错误信息的响应：
      ```json
      {
        "type": "WebSocketMessageType.CALL_TOOL_RESPONSE",
        "responseToRequestId": "requestId",
        "payload": {
          "status": "error",
          "message": "ERROR_MESSAGES.TOOL_EXECUTION_FAILED",
          "error": "error instanceof Error ? error.message : String(error)"
        }
      }
      ```

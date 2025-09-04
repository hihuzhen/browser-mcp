/**
 * WebSocket 通信消息类型定义
 */

export enum WebSocketMessageType {
    // 心跳检测，用于判断 WebSocket 服务是否正常
    PING = 'ping',
    PONG = 'pong',
    // 从服务端发来的工具调用请求
    CALL_TOOL = 'call_tool',
    // 返回给服务端的工具调用响应
    CALL_TOOL_RESPONSE = 'call_tool_response',
    // 错误消息
    ERROR = 'error'
}

export enum ServerMessageType {
    // 内部消息类型
    PING_WEBSOCKET = 'ping_websocket',
    GET_WEBSOCKET_STATUS = 'get_websocket_status',
    // 连接 WebSocket
    CONNECT = 'connect_websocket',
    // 断开 WebSocket 连接
    DISCONNECT = 'disconnect_websocket'
}

// Tool action message types (for chrome.runtime.sendMessage)
export const TOOL_MESSAGE_TYPES = {
    // Screenshot related
    SCREENSHOT_PREPARE_PAGE_FOR_CAPTURE: 'preparePageForCapture',
    SCREENSHOT_GET_PAGE_DETAILS: 'getPageDetails',
    SCREENSHOT_GET_ELEMENT_DETAILS: 'getElementDetails',
    SCREENSHOT_SCROLL_PAGE: 'scrollPage',
    SCREENSHOT_RESET_PAGE_AFTER_CAPTURE: 'resetPageAfterCapture',

    // Web content fetching
    WEB_FETCHER_GET_HTML_CONTENT: 'getHtmlContent',
    WEB_FETCHER_GET_TEXT_CONTENT: 'getTextContent',

    // User interactions
    CLICK_ELEMENT: 'clickElement',
    FILL_ELEMENT: 'fillElement',
    SIMULATE_KEYBOARD: 'simulateKeyboard',

    // Interactive elements
    GET_INTERACTIVE_ELEMENTS: 'getInteractiveElements',

    // Network requests
    NETWORK_SEND_REQUEST: 'sendPureNetworkRequest',

} as const;


export interface WebSocketMessage<P = any, E = any> {
    type?: WebSocketMessageType;
    responseToRequestId?: string;
    requestId?: string;
    payload?: P;
    error?: E;
}
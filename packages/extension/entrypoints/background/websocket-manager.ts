/**
 * WebSocket管理器 - 负责与外部服务端的WebSocket通信管理
 */

import {WebSocketMessageType, WebSocketMessage, ServerMessageType} from '@/common/message-types';
import { handleCallTool } from './tools';

// WebSocket状态管理接口
interface WebSocketStatus {
    isConnected: boolean;
    shouldConnect: boolean;
    url?: string;
    lastUpdated: number;
}

// 常量定义
const TEN_SECONDS_MS = 10 * 1000;
const DEFAULT_WEBSOCKET_URL = 'ws://localhost:18765';
const STORAGE_KEYS = {
    WEBSOCKET_STATUS: 'websocketStatus',
    WEBSOCKET_URL: 'websocketUrl'
};

// 错误消息定义
const ERROR_MESSAGES = {
    CONNECTION_FAILED: 'Failed to connect to WebSocket server',
    DISCONNECTED: 'WebSocket connection disconnected',
    MESSAGE_PROCESS_FAILED: 'Failed to process WebSocket message',
    INVALID_MESSAGE: 'Invalid message format received',
    TOOL_EXECUTION_FAILED: 'Tool execution failed',
};

// 成功消息定义
const SUCCESS_MESSAGES = {
    CONNECTED: 'WebSocket connected successfully',
    MESSAGE_SENT: 'Message sent successfully',
    TOOL_EXECUTED: 'Tool executed successfully',
};

/**
 * WebSocket管理器类 - 封装WebSocket连接、消息处理和重连逻辑
 */
class WebSocketManager {
    private ws: WebSocket | null = null;
    private messageQueue: WebSocketMessage[] = [];
    private currentStatus: WebSocketStatus = {
        isConnected: false,
        shouldConnect: false, // 默认不自动连接
        url: DEFAULT_WEBSOCKET_URL,
        lastUpdated: Date.now()
    };
    private keepAliveIntervalId: ReturnType<typeof setInterval> | null = null;
    private reconnectTimeoutId: ReturnType<typeof setTimeout> | null = null;
    private reconnectAttempts = 0;
    private maxReconnectAttempts = 10;
    private minReconnectDelay = 1000; // 最小重连延迟1秒
    private maxReconnectDelay = 30000; // 最大重连延迟30秒

    /**
     * 构造函数
     */
    constructor() {
        // 构造函数不能是异步的，所以这里不直接调用异步方法
        // 初始化工作会在外部进行
    }

    /**
     * 初始化WebSocket管理器
     */
    public async initialize(): Promise<void> {
        try {
            await this.loadStatus();
        } catch (error) {
            console.error('Failed to initialize WebSocket manager:', error);
        }
    }

    /**
     * 保存WebSocket状态到chrome.storage
     */
    private async saveStatus(status: WebSocketStatus): Promise<void> {
        try {
            await chrome.storage.local.set({[STORAGE_KEYS.WEBSOCKET_STATUS]: status});
        } catch (error) {
            console.error('Failed to save WebSocket status:', error);
        }
    }

    /**
     * 从chrome.storage加载WebSocket状态
     */
    public async loadStatus(): Promise<void> {
        try {
            const result = await chrome.storage.local.get([STORAGE_KEYS.WEBSOCKET_STATUS]);
            if (result[STORAGE_KEYS.WEBSOCKET_STATUS]) {
                this.currentStatus = result[STORAGE_KEYS.WEBSOCKET_STATUS];
            }
        } catch (error) {
            console.error('Failed to load WebSocket status:', error);
            this.currentStatus = {
                isConnected: false,
                shouldConnect: false,
                url: DEFAULT_WEBSOCKET_URL,
                lastUpdated: Date.now()
            };
        }
    }

    /**
     * 判断WebSocket是否成功连接
     */
    public isConnected(): boolean {
        return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
    }

    /**
     * 获取当前WebSocket状态
     */
    public getStatus(): WebSocketStatus {
        return {...this.currentStatus};
    }

    /**
     * 设置是否应该保持连接
     */
    public setShouldConnect(shouldConnect: boolean): void {
        this.currentStatus.shouldConnect = shouldConnect;
        this.saveStatus(this.currentStatus).catch(error => {
            console.error('Failed to save WebSocket status:', error);
        });
    }

    /**
     * 连接到WebSocket服务器
     */
    public connect(url: string = DEFAULT_WEBSOCKET_URL): void {
        // 如果已经连接，直接返回
        if (this.isConnected()) {
            return;
        }

        try {
            // 清除重连定时器
            this.clearReconnectTimeout();

            this.ws = new WebSocket(url);
            this.currentStatus.url = url;

            this.ws.onopen = this.handleOpen.bind(this);
            this.ws.onmessage = this.handleMessage.bind(this);
            this.ws.onclose = this.handleClose.bind(this);
            this.ws.onerror = this.handleError.bind(this);
        } catch (error) {
            console.error(ERROR_MESSAGES.CONNECTION_FAILED, error);
            // 发生错误时也尝试重连
            this.attemptReconnect();
        }
    }

    /**
     * 断开WebSocket连接
     */
    public disconnect(): void {
        this.setShouldConnect(false);

        // 清除重连定时器和保活定时器
        this.clearReconnectTimeout();
        this.clearKeepAliveInterval();

        if (this.ws) {
            this.ws.close();
        }
    }

    /**
     * 发送消息到WebSocket服务器
     */
    public sendMessage(message: WebSocketMessage): void {
        try {
            if (this.isConnected() && this.ws) {
                const messageString = JSON.stringify(message);
                this.ws.send(messageString);
                return;
            }

            // 将消息排队，等连接建立后再发送
            this.enqueueMessage(message);
        } catch (error) {
            console.error('Failed to send WebSocket message:', error);
            this.enqueueMessage(message);
        }
    }

    /**
     * 将消息加入队列
     */
    private enqueueMessage(message: WebSocketMessage): void {
        // 限制队列大小，防止内存溢出
        if (this.messageQueue.length >= 100) {
            console.warn('Message queue is full, removing oldest message');
            this.messageQueue.shift();
        }
        this.messageQueue.push(message);
    }

    /**
     * 处理队列中的消息
     */
    private processMessageQueue(): void {
        if (!this.isConnected() || !this.ws) {
            return;
        }

        // 一次只处理一个消息
        if (this.messageQueue.length > 0) {
            const message = this.messageQueue.shift();
            if (message && this.isConnected() && this.ws) {
                try {
                    this.ws.send(JSON.stringify(message));
                } catch (error) {
                    console.error('Failed to send queued message:', error);
                    // 重新加入队列开头
                    this.messageQueue.unshift(message);
                }
            }
        }

        // 如果还有消息，继续处理
        if (this.messageQueue.length > 0) {
            setTimeout(() => this.processMessageQueue(), 10);
        }
    }

    /**
     * 尝试重新连接WebSocket - 使用指数退避算法
     */
    private attemptReconnect(): void {
        // 清除现有的重连定时器
        this.clearReconnectTimeout();

        // 如果应该连接但当前未连接，则设置重连
        if (this.currentStatus.shouldConnect && !this.isConnected()) {
            // 指数退避算法计算重连延迟
            this.reconnectAttempts++;
            if (this.reconnectAttempts > this.maxReconnectAttempts) {
                console.warn('Max reconnection attempts reached, stopping reconnection');
                return;
            }

            const delay = Math.min(
                this.minReconnectDelay * Math.pow(2, this.reconnectAttempts - 1),
                this.maxReconnectDelay
            );

            console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

            this.reconnectTimeoutId = setTimeout(() => {
                if (this.currentStatus.url) {
                    this.connect(this.currentStatus.url);
                }
            }, delay);
        }
    }

    /**
     * 保持WebSocket连接活跃
     */
    private keepAlive(): void {
        // 清除之前的定时器
        this.clearKeepAliveInterval();

        // 设置新的保活定时器
        this.keepAliveIntervalId = setInterval(() => {
            // 检查是否应该连接但未连接
            if (this.currentStatus.shouldConnect && !this.isConnected()) {
                // 尝试重新连接
                if (this.currentStatus.url) {
                    this.connect(this.currentStatus.url);
                }
            } else if (this.isConnected() && this.ws) {
                // 发送心跳消息
                this.sendMessage({type: WebSocketMessageType.PING});
            } else {
                // 清除定时器
                this.clearKeepAliveInterval();
            }
        }, TEN_SECONDS_MS);
    }

    /**
     * 清除重连定时器
     */
    private clearReconnectTimeout(): void {
        if (this.reconnectTimeoutId) {
            clearTimeout(this.reconnectTimeoutId);
            this.reconnectTimeoutId = null;
        }
    }

    /**
     * 清除保活定时器
     */
    private clearKeepAliveInterval(): void {
        if (this.keepAliveIntervalId) {
            clearInterval(this.keepAliveIntervalId);
            this.keepAliveIntervalId = null;
        }
    }

    /**
     * 处理WebSocket连接打开事件
     */
    private handleOpen(): void {
        this.currentStatus = {
            isConnected: true,
            shouldConnect: this.currentStatus.shouldConnect, // 保持shouldConnect状态
            url: this.currentStatus.url,
            lastUpdated: Date.now()
        };
        this.saveStatus(this.currentStatus).catch(error => {
            console.error('Failed to save WebSocket status:', error);
        });
        this.reconnectAttempts = 0; // 重置重连尝试次数

        console.log(SUCCESS_MESSAGES.CONNECTED);

        // 处理队列中的消息
        this.processMessageQueue();

        // 启动保活机制
        this.keepAlive();
    }

    /**
     * 处理接收到的消息
     */
    private async handleMessage(event: MessageEvent): Promise<void> {
        try {
            // 验证消息格式
            if (typeof event.data !== 'string') {
                console.error('Invalid message format: data is not a string');
                // 尝试提取请求ID以发送错误响应
                try {
                    const messageObj = JSON.parse(event.data);
                    this.sendMessage({
                        type: WebSocketMessageType.ERROR,
                        responseToRequestId: messageObj?.requestId,
                        error: ERROR_MESSAGES.INVALID_MESSAGE
                    });
                } catch (innerError) {
                    console.error('Failed to parse error message:', innerError);
                }
                return;
            }

            // 检查消息大小
            if (event.data.length > 1024 * 1024) { // 1MB限制
                console.error('Message too large');
                // 尝试提取请求ID以发送错误响应
                try {
                    const messageObj = JSON.parse(event.data);
                    this.sendMessage({
                        type: WebSocketMessageType.ERROR,
                        responseToRequestId: messageObj?.requestId,
                        error: ERROR_MESSAGES.INVALID_MESSAGE
                    });
                } catch (innerError) {
                    console.error('Failed to parse error message:', innerError);
                }
                return;
            }

            const message: WebSocketMessage = JSON.parse(event.data);

            // 验证消息结构
            if (!message.type) {
                console.error('Message missing required field: type');
                // 尝试提取请求ID以发送错误响应
                try {
                    const messageObj = JSON.parse(event.data);
                    this.sendMessage({
                        type: WebSocketMessageType.ERROR,
                        responseToRequestId: messageObj?.requestId,
                        error: ERROR_MESSAGES.INVALID_MESSAGE
                    });
                } catch (innerError) {
                    console.error('Failed to parse error message:', innerError);
                }
                return;
            }

            console.log('Received WebSocket message:', message);
            await this.processReceivedMessage(message);
        } catch (error) {
            console.error(ERROR_MESSAGES.MESSAGE_PROCESS_FAILED, error);
            // 尝试提取请求ID以发送错误响应
            try {
                const messageObj = JSON.parse(event.data);
                this.sendMessage({
                    type: WebSocketMessageType.ERROR,
                    responseToRequestId: messageObj?.requestId,
                    error: ERROR_MESSAGES.INVALID_MESSAGE
                });
            } catch (innerError) {
                console.error('Failed to parse error message:', innerError);
            }
        }
    }

    /**
     * 处理接收到的具体消息
     */
    private async processReceivedMessage(message: WebSocketMessage): Promise<void> {
        // 根据消息类型处理
        switch (message.type) {
            case WebSocketMessageType.PING:
                this.sendMessage({
                    type: WebSocketMessageType.PONG,
                    responseToRequestId: message.requestId
                });
                break;

            case WebSocketMessageType.PONG:
                // 处理心跳响应
                console.log('Received PONG message:', message);
                break;

            case WebSocketMessageType.CALL_TOOL:
                const requestId = message.requestId;
                try {
                    const result = await handleCallTool(message.payload);
                    this.sendMessage({
                        type: WebSocketMessageType.CALL_TOOL_RESPONSE,
                        responseToRequestId: requestId,
                        payload: {
                            status: 'success',
                            message: SUCCESS_MESSAGES.TOOL_EXECUTED,
                            data: result,
                        },
                    });
                } catch (error) {
                    this.sendMessage({
                        type: WebSocketMessageType.CALL_TOOL_RESPONSE,
                        responseToRequestId: requestId,
                        payload: {
                            status: 'error',
                            message: ERROR_MESSAGES.TOOL_EXECUTION_FAILED,
                            error: error instanceof Error ? error.message : String(error),
                        },
                    });
                }
                break;

            default:
                console.warn('Unknown message type:', message.type);
                this.sendMessage({
                    type: WebSocketMessageType.ERROR,
                    responseToRequestId: message.requestId,
                    error: `Unknown message type: ${message.type}`
                });
        }
    }

    /**
     * 处理WebSocket连接关闭事件
     */
    private handleClose(): void {
        this.currentStatus = {
            isConnected: false,
            shouldConnect: this.currentStatus.shouldConnect,
            url: this.currentStatus.url,
            lastUpdated: Date.now()
        };
        this.saveStatus(this.currentStatus).catch(error => {
            console.error('Failed to save WebSocket status:', error);
        });

        console.log(ERROR_MESSAGES.DISCONNECTED);
        this.ws = null;

        // 如果应该保持连接，则尝试重连
        this.attemptReconnect();
    }

    /**
     * 处理WebSocket错误事件
     */
    private handleError(error: Event): void {
        console.error('WebSocket error:', error);
        this.sendMessage({
            type: WebSocketMessageType.ERROR,
            error: ERROR_MESSAGES.CONNECTION_FAILED
        });
    }
}

/**
 * 创建全局WebSocket管理器实例
 */
const globalWsManager = new WebSocketManager();

/**
 * 初始化WebSocket监听器并加载初始状态
 */
export const initWebSocketListener = () => {
    // 从存储中初始化WebSocket状态
    globalWsManager.initialize()
        .then(() => {
            const status = globalWsManager.getStatus();
            // 如果状态显示应该连接，则尝试连接
            if (status.shouldConnect && status.url) {
                globalWsManager.connect(status.url);
            }
        })
        .catch((error) => {
            console.error('Failed to load WebSocket status:', error);
        });

    // 监听来自运行时的消息
    chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
        if (message.type === ServerMessageType.PING_WEBSOCKET) {
            const connected = globalWsManager.isConnected();
            sendResponse({connected});
            return true;
        }

        if (message.type === ServerMessageType.GET_WEBSOCKET_STATUS) {
            sendResponse({
                success: true,
                websocketStatus: globalWsManager.getStatus(),
                connected: globalWsManager.isConnected(),
            });
            return true;
        }

        // 添加对 CONNECT 和 DISCONNECT 消息的处理
        if (message.type === ServerMessageType.CONNECT) {
            // 处理连接请求
            globalWsManager.setShouldConnect(true);

            if (message.payload?.url) {
                globalWsManager.connect(message.payload.url);
            } else {
                globalWsManager.connect();
            }
            return true;
        }

        if (message.type === ServerMessageType.DISCONNECT) {
            // 处理断开连接请求
            globalWsManager.disconnect();
            return true;
        }

        return false;
    });
};

/**
 * 导出WebSocket管理器方法，保持向后兼容性
 * export function isWebSocketConnected(): boolean {
 *     return globalWsManager.isConnected();
 * }
 *
 * export function connectWebSocket(url?: string): void {
 *     globalWsManager.connect(url || DEFAULT_WEBSOCKET_URL);
 * }
 *
 * export function disconnectWebSocket(): void {
 *     globalWsManager.disconnect();
 * }
 *
 * export function sendMessage(message: WebSocketMessage): void {
 *     globalWsManager.sendMessage(message);
 * }
 */

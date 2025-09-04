import {ServerMessageType} from '@/common/message-types';


// 获取并更新连接状态
async function updateConnectionStatus() {
    const response = await chrome.runtime.sendMessage({type: ServerMessageType.GET_WEBSOCKET_STATUS});
    const status = response?.websocketStatus || {isConnected: false};

    const toggleButton = document.getElementById('toggle-connection') as HTMLButtonElement;
    toggleButton.textContent = status.isConnected ? '断开' : '连接';
    toggleButton.classList.toggle('disconnect', status.isConnected);
}

// 切换连接状态
async function toggleConnection() {
    const response = await chrome.runtime.sendMessage({type: ServerMessageType.GET_WEBSOCKET_STATUS});
    const status = response?.websocketStatus || {isConnected: false};

    if (status.isConnected) {
        await chrome.runtime.sendMessage({type: ServerMessageType.DISCONNECT});
    } else {
        await chrome.runtime.sendMessage({
          type: ServerMessageType.CONNECT,
        });
    }
}

// 初始化popup
document.addEventListener('DOMContentLoaded', () => {
    // 初始状态更新
    updateConnectionStatus();

    // 绑定事件
    const toggleButton = document.getElementById('toggle-connection') as HTMLButtonElement;
    toggleButton.addEventListener('click', toggleConnection);

    // 定期更新状态
    setInterval(updateConnectionStatus, 1000);
});
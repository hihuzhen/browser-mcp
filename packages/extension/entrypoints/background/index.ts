import { initWebSocketListener } from './websocket-manager';

export default defineBackground(() => {
  console.log('Background service worker started');
  // 初始化WebSocket监听器
  initWebSocketListener();
});
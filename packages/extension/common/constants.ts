/**
 * Chrome Extension Constants
 * Centralized configuration values and magic constants
 */

// Timeouts and Delays (in milliseconds)
export const TIMEOUTS = {
  DEFAULT_WAIT: 1000,
  NETWORK_CAPTURE_MAX: 30000,
  NETWORK_CAPTURE_IDLE: 3000,
  SCREENSHOT_DELAY: 100,
  KEYBOARD_DELAY: 50,
  CLICK_DELAY: 100,
} as const;

// Error Messages
export const ERROR_MESSAGES = {
  NATIVE_CONNECTION_FAILED: 'Failed to connect to native host',
  NATIVE_DISCONNECTED: 'Native connection disconnected',
  SERVER_STATUS_LOAD_FAILED: 'Failed to load server status',
  SERVER_STATUS_SAVE_FAILED: 'Failed to save server status',
  TOOL_EXECUTION_FAILED: 'Tool execution failed',
  INVALID_PARAMETERS: 'Invalid parameters provided',
  PERMISSION_DENIED: 'Permission denied',
  TAB_NOT_FOUND: 'Tab not found',
  ELEMENT_NOT_FOUND: 'Element not found',
  NETWORK_ERROR: 'Network error occurred',
} as const;


export enum ExecutionWorld {
  ISOLATED = 'ISOLATED',
  MAIN = 'MAIN',
}

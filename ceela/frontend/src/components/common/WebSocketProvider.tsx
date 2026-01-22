import { notify } from '@/utils/notify';
import React, { createContext, ReactNode, useContext, useEffect, useState } from 'react';

// Define the shape of our WebSocket context
interface WebSocketContextType {
    socket: WebSocket | null;
    connected: boolean;
    lastMessage: any | null;
    sendMessage: (message: any) => void;
    reconnect: () => void;
}

// Create the context with default values
const WebSocketContext = createContext<WebSocketContextType>({
    socket: null,
    connected: false,
    lastMessage: null,
    sendMessage: () => { },
    reconnect: () => { },
});

// Custom hook for using the WebSocket context
export const useWebSocket = () => useContext(WebSocketContext);

interface WebSocketProviderProps {
    children: ReactNode;
    path?: string; // Optional path to append to the base WS URL
    onMessage?: (data: any) => void; // Optional callback for message handling
    autoReconnect?: boolean; // Whether to auto reconnect on disconnect
    reconnectInterval?: number; // Reconnect interval in milliseconds
}

export const WebSocketProvider: React.FC<WebSocketProviderProps> = ({
    children,
    path = 'ws',
    onMessage,
    autoReconnect = true,
    reconnectInterval = 5000,
}) => {
    const [socket, setSocket] = useState<WebSocket | null>(null);
    const [connected, setConnected] = useState<boolean>(false);
    const [lastMessage, setLastMessage] = useState<any | null>(null); const connectWebSocket = () => {
        // Get user ID from local storage
        const user = localStorage.getItem('userProfile') || 'anonymous';
        const userId = JSON.parse(user).id || 'anonymous';
        const wsUrl = `${process.env.NEXT_PUBLIC_WS_ENDPOINT}/ws/${userId}`;

        console.log('WebSocket URL:', wsUrl);
        try {
            console.log('Connecting to WebSocket:', wsUrl);
            const ws = new WebSocket(wsUrl);

            ws.onopen = () => {
                console.log('WebSocket connected');
                setConnected(true);
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    setLastMessage(data);
                    if (onMessage) {
                        onMessage(data);
                    }
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                    setLastMessage(event.data); // Store raw data if parsing fails
                }
            };

            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
            };

            ws.onclose = (event) => {
                console.log('WebSocket disconnected:', event.code, event.reason);
                setConnected(false);

                if (autoReconnect) {
                    console.log(`Reconnecting in ${reconnectInterval / 1000} seconds...`);
                    setTimeout(connectWebSocket, reconnectInterval);
                }
            };

            setSocket(ws);

            // Clean up function
            return () => {
                ws.close();
            };
        } catch (error) {
            console.error('Failed to create WebSocket connection:', error);
            notify('Error al crear conexión WebSocket', 'error');

            // Auto reconnect if enabled
            if (autoReconnect) {
                console.log(`Attempting to reconnect in ${reconnectInterval / 1000} seconds...`);
                setTimeout(connectWebSocket, reconnectInterval);
            }
        }
    };

    // Connect on component mount
    useEffect(() => {
        const cleanup = connectWebSocket();

        // Clean up on unmount
        return () => {
            if (cleanup) cleanup();
            if (socket && socket.readyState === WebSocket.OPEN) {
                socket.close();
            }
        };
    }, [path]); // Reconnect if path changes

    // Function to send messages
    const sendMessage = (message: any) => {
        if (socket && connected) {
            const messageString = typeof message === 'string' ? message : message;
            console.log('Sending message:', messageString);
            socket.send(JSON.stringify(messageString));
        } else {
            console.error('Cannot send message: WebSocket is not connected');
        }
    };

    // Function to manually reconnect
    const reconnect = () => {
        if (socket) {
            socket.close();
        }
        connectWebSocket();
    };

    return (
        <WebSocketContext.Provider value={{ socket, connected, lastMessage, sendMessage, reconnect }}>
            {children}
        </WebSocketContext.Provider>
    );
};

export default WebSocketProvider;

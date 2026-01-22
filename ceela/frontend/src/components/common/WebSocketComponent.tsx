'use client'
import { notify } from '@/utils/notify';
import React, { forwardRef, useEffect, useImperativeHandle, useState } from 'react';
import { Card, Spinner } from 'react-bootstrap';
import CustomButton from './CustomButton';
import { useWebSocket, WebSocketProvider } from './WebSocketProvider';

interface WebSocketComponentProps {
    path?: string; // Optional path to append to the WebSocket URL
    onMessageReceived?: (data: any) => void; // Callback to return data to parent component
    onConnectionChange?: (status: boolean) => void; // Optional callback for connection status changes
}

/**
 * Notification message interface
 */
interface NotificationMessage {
    id: string;
    type: string;
    message: string;
    timestamp: string;
    payload?: any;
    read: boolean;
}

/**
 * WebSocketComponent for handling notifications.
 * This component connects to a WebSocket server and processes incoming notifications.
 */

const WebSocketComponent = forwardRef<any, WebSocketComponentProps>(function WebSocketComponent({
    path = 'ws',
    onMessageReceived,
    onConnectionChange
}, ref) {
    const [notifications, setNotifications] = useState<NotificationMessage[]>([]);
    const [rawMessages, setRawMessages] = useState<any[]>([]);

    // Permitir limpiar notificaciones desde el padre
    useImperativeHandle(ref, () => ({
        clearNotifications: () => setNotifications([]),
    }));

    // Process incoming messages from WebSocket
    const handleMessage = (data: any) => {
        setRawMessages(prev => [
            { timestamp: new Date().toISOString(), data: data },
            ...prev
        ].slice(0, 20)); // Keep last 20 raw messages

        try {
            // Parse the message if it's a string
            const parsedData = typeof data === 'string' ? JSON.parse(data) : data;
            if (parsedData.type === 'notification') {
                const newNotification: NotificationMessage = {
                    id: Date.now().toString(),
                    type: 'notification',
                    message: parsedData.message || 'Nueva notificación',
                    timestamp: new Date().toISOString(),
                    payload: parsedData.payload,
                    read: false
                };

                setNotifications(prev => [newNotification, ...prev].slice(0, 50)); // Keep last 50 notifications

                notify(parsedData.message || 'Nueva notificación', parsedData.notificationType || 'info');
            }
            onMessageReceived?.(parsedData);
        } catch (error) {
            console.error('Error processing WebSocket message:', error);
        }
    }
    return (
        <WebSocketProvider
            path={path}
            onMessage={handleMessage}
            autoReconnect={true}
        >
            <NotificationDisplay
                notifications={notifications}
                rawMessages={rawMessages}
                onConnectionChange={onConnectionChange}
            />
        </WebSocketProvider>
    );
});

interface NotificationDisplayProps {
    notifications: NotificationMessage[];
    rawMessages?: any[];
    onConnectionChange?: (status: boolean) => void;
}

/**
 * Component to display notifications and connection status
 */
const NotificationDisplay: React.FC<NotificationDisplayProps> = ({
    notifications,
    rawMessages,
    onConnectionChange
}) => {
    const { connected, reconnect } = useWebSocket();
    const [expanded, setExpanded] = useState(false);
    const [showAllNotifications, setShowAllNotifications] = useState(false);

    // Notify parent component of connection status changes
    useEffect(() => {
        if (onConnectionChange) {
            onConnectionChange(connected);
        }
    }, [connected, onConnectionChange]);

    const toggleExpanded = () => {
        setExpanded(!expanded);
    };

    const toggleAllNotifications = () => {
        setShowAllNotifications(!showAllNotifications);
    };

    // Filter notifications - show all or only unread based on toggle
    const displayedNotifications = showAllNotifications
        ? notifications
        : notifications.filter(n => !n.read).length > 0
            ? notifications.filter(n => !n.read)
            : notifications.slice(0, 5);

    return (
        <div className="notification-component shadow-sm">
            {/* Connection status indicator - only shown when disconnected */}
            {!connected && (
                <div className="notification-connection-status p-3 mb-3 border rounded bg-danger bg-opacity-10 border-danger text-danger">
                    <div className="d-flex align-items-center justify-content-between">
                        <div className="d-flex align-items-center">
                            <i className="bi bi-exclamation-triangle-fill me-2"></i>
                            <span>
                                Desconectado del servidor de notificaciones
                                <span className="badge bg-danger ms-2 animate__animated animate__pulse animate__infinite">•</span>
                            </span>
                        </div>                        <CustomButton onClick={reconnect} variant="save" className="ms-2">
                            <i className="bi bi-arrow-clockwise me-1"></i> Reconectar
                        </CustomButton>
                    </div>
                    <div className="d-flex justify-content-center align-items-center mt-2">
                        <Spinner animation="border" variant="danger" size="sm" role="status" />
                        <span className="ms-2 fw-light">Intentando reconectar automáticamente...</span>
                    </div>
                </div>
            )}            {/* Notifications card/panel */}
            {connected && (
                <Card className="notification-panel shadow-sm border-0">
                    <Card.Header
                        className="d-flex justify-content-between align-items-center cursor-pointer bg-secondary text-white"
                        onClick={toggleExpanded}
                    >
                        <div className="d-flex align-items-center">
                            <i className="bi bi-activity me-2"></i>
                            <span className="fw-bold">Estado</span>
                            {notifications.filter(n => !n.read).length > 0 && (
                                <span className="ms-2 badge bg-danger rounded-pill">
                                    {notifications.filter(n => !n.read).length}
                                </span>
                            )}
                        </div>
                        <div>
                            <i className={`bi bi-chevron-${expanded ? 'down' : 'up'}`}></i>
                        </div>
                    </Card.Header>

                    {expanded && (
                        <Card.Body className="notification-list p-0" style={{ maxHeight: '350px', overflowY: 'auto' }}>
                            {notifications.length === 0 ? (
                                <div className="text-center text-muted py-4">
                                    <i className="bi bi-inbox fs-3 d-block mb-2"></i>
                                    <span>No hay notificaciones</span>
                                </div>
                            ) : (
                                <>
                                    <div className="list-group list-group-flush">
                                        {displayedNotifications.map(notification => (
                                            <div
                                                key={notification.id}
                                                className={`list-group-item list-group-item-action ${!notification.read ? 'list-group-item-light' : ''}`}
                                            >
                                                <div className="d-flex justify-content-between align-items-center">
                                                    <h6 className="mb-1">{notification.message}</h6>
                                                    <small className="text-muted badge bg-light text-dark">
                                                        {new Date(notification.timestamp).toLocaleTimeString()}
                                                    </small>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                              </>
                            )}
                        </Card.Body>)}
                </Card>
            )}
        </div>
    );
};

export default React.memo(WebSocketComponent);
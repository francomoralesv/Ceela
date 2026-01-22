import React, { useState } from 'react';
import { Col, Row } from 'react-bootstrap';

interface ErrorDetail {
    message: string;
    context: string;
    response?: {
        data?: {
            detail?: string;
        };
    };
}

interface ErrorDetailsAccordionProps {
    errors: ErrorDetail[];
}

export const ErrorDetailsAccordion: React.FC<ErrorDetailsAccordionProps> = ({ errors }) => {
    // State to track which groups are expanded
    const [expandedGroups, setExpandedGroups] = useState<{ [key: string]: boolean }>({});

    // Group errors by context for better readability
    const errorGroups: { [key: string]: ErrorDetail[] } = {};
    errors.forEach(error => {
        // Extract main context (e.g., "Room AU: Creating walls" -> "Room AU")
        const mainContext = error.context.split(':')[0];
        if (!errorGroups[mainContext]) {
            errorGroups[mainContext] = [];
        }
        errorGroups[mainContext].push(error);
    });

    // Toggle group expansion
    const toggleGroup = (groupKey: string) => {
        setExpandedGroups(prev => ({
            ...prev,
            [groupKey]: !prev[groupKey]
        }));
    };

    // Extract meaningful error detail from error messages or response objects
    const getErrorDetail = (error: ErrorDetail): string => {
        // Check for backend API detail message in error.response
        if (error.response?.data?.detail) {
            return error.response.data.detail;
        }

        // Try to extract detail from error message for Axios errors
        if (error.message) {
            // Try to find "detail: " pattern in the error message
            const detailMatch = error.message.match(/detail[":"'\s]+([^"'}\]]+)/i);
            if (detailMatch && detailMatch[1]) {
                return detailMatch[1].trim();
            }

            // Try to parse JSON from the message if it contains JSON
            const jsonMatch = error.message.match(/(\{.*\})/);
            if (jsonMatch) {
                try {
                    const jsonObj = JSON.parse(jsonMatch[0]);
                    if (jsonObj.detail) {
                        return jsonObj.detail;
                    }
                } catch (e) {
                    // JSON parsing failed, continue with other methods
                }
            }

            // Return the message if it contains the word "detail"
            if (error.message.includes('detail')) {
                return error.message;
            }
        }

        // Default to the original error message
        return error.message;
    };

    return (
        <Row className="mt-2">
            <Col>
                <div className="alert alert-danger">
                    <h6>Detalles de errores ({errors.length}):</h6>

                    {/* Custom accordion implementation */}
                    <div>
                        {Object.entries(errorGroups).map(([context, groupErrors], groupIndex) => (
                            <div className="card mb-2" key={groupIndex}>
                                <div
                                    className="card-header d-flex justify-content-between align-items-center"
                                    onClick={() => toggleGroup(context)}
                                    style={{ cursor: 'pointer' }}
                                >
                                    <span>{context} - {groupErrors.length} {groupErrors.length === 1 ? 'error' : 'errores'}</span>
                                    <span>{expandedGroups[context] ? '▼' : '▶'}</span>
                                </div>

                                {expandedGroups[context] && (
                                    <div className="card-body p-0">
                                        <ul className="list-group list-group-flush">
                                            {groupErrors.map((error, errorIndex) => {
                                                const errorDetail = getErrorDetail(error);
                                                return (
                                                    <li className="list-group-item" key={errorIndex}>
                                                        <div className="fw-bold text-danger">{errorDetail}</div>
                                                    </li>
                                                );
                                            })}
                                        </ul>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            </Col>
        </Row>
    );
};

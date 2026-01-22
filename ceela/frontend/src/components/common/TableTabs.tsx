import { TableTabStyle } from '@/styles/TabStyle';
import React, { useEffect, useRef, useState } from 'react';

interface TabItem {
    key: string;
    label: string;
}

interface TableTabsProps {
    tabs: TabItem[];
    initialTab?: string;
    onTabChange?: (tab: string) => void;
    className?: string;
}

/**
 * TableTabs - Un componente reutilizable para tabs en tablas
 * Utiliza el mismo estilo que HorizontalTabs pero optimizado para tablas
 */
const TableTabs: React.FC<TableTabsProps> = ({
    tabs,
    initialTab,
    onTabChange,
    className = ''
}) => {
    const [activeTab, setActiveTab] = useState(initialTab || (tabs.length > 0 ? tabs[0].key : ''));
    const tabsContainerRef = useRef<HTMLUListElement>(null);
    // Create a single ref to hold all button elements
    const buttonsRef = useRef<HTMLButtonElement[]>([]);

    const handleTabChange = (tab: string) => {
        setActiveTab(tab);
        if (onTabChange) {
            onTabChange(tab);
        }
    };

    // Effect to equalize button heights
    useEffect(() => {
        const equalizeButtonHeights = () => {
            const buttons = buttonsRef.current.filter(Boolean);
            if (buttons.length === 0) return;

            // Reset heights first
            buttons.forEach(btn => {
                btn.style.height = 'auto';
            });

            // Calculate the max height
            const maxHeight = Math.max(...buttons.map(btn => btn.offsetHeight));

            // Apply max height to all buttons
            if (maxHeight > 0) {
                buttons.forEach(btn => {
                    btn.style.height = `${maxHeight}px`;
                });
            }
        };

        // Ensure we run after the DOM has updated
        requestAnimationFrame(() => {
            equalizeButtonHeights();
        });

        // Run when window is resized
        window.addEventListener('resize', equalizeButtonHeights);

        return () => {
            window.removeEventListener('resize', equalizeButtonHeights);
        };
    }, [tabs, activeTab]); // Re-run when tabs or active tab changes

    // Reset the refs array when tabs change
    useEffect(() => {
        buttonsRef.current = [];
    }, [tabs]);

    // Function to assign ref to button element
    const setButtonRef = (element: HTMLButtonElement | null, index: number) => {
        if (element) {
            buttonsRef.current[index] = element;
        }
    };

    return (
        <TableTabStyle className={className}>
            <ul className="horizontal-tabs-list" ref={tabsContainerRef}>
                {tabs.map((item, index) => (
                    <li key={item.key} className="tab-item">
                        <button
                            ref={(el) => setButtonRef(el, index)}
                            className={activeTab === item.key ? "tab-button active" : "tab-button"}
                            onClick={() => handleTabChange(item.key)}
                        >
                            <span className="tab-number">{index + 1}.</span>
                            {item.label}
                        </button>
                    </li>
                ))}
            </ul>
        </TableTabStyle>
    );
};

export default TableTabs;

import { TabStyle } from '@/styles/TabStyle';
import React, { useEffect, useRef } from 'react';

interface TabItem {
    key: string;
    label: string;
}

interface HorizontalTabsProps {
    tabs: TabItem[];
    currentTab: string;
    onTabChange: (tab: string) => void;
    className?: string;
}

const HorizontalTabs: React.FC<HorizontalTabsProps> = ({
    tabs,
    currentTab,
    onTabChange,
    className = ''
}) => {
    const tabsContainerRef = useRef<HTMLUListElement>(null);
    // Create a single ref to hold all button elements
    const buttonsRef = useRef<HTMLButtonElement[]>([]);

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
    }, [tabs, currentTab]); // Re-run when tabs or current tab changes

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
        <TabStyle className={className}>
            <ul className="horizontal-tabs-list" ref={tabsContainerRef}>
                {tabs.map((item, index) => (
                    <li key={item.key} className="tab-item">
                        <button
                            ref={(el) => setButtonRef(el, index)}
                            className={currentTab === item.key ? "tab-button active" : "tab-button"}
                            onClick={() => onTabChange(item.key)}
                        >
                            <span className="tab-number">{index + 1}</span>
                            {item.label}
                        </button>
                    </li>
                ))}
            </ul>
        </TabStyle>
    );
};

export default HorizontalTabs;

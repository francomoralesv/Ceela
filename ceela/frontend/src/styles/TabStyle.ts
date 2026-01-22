import { COLORS } from '@/constants/colors';
import styled from 'styled-components';

export const TabStyle = styled.div`
  .horizontal-tabs-list {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    padding: 0;
    list-style: none;
    gap: 0;
    margin: 0 0 20px 0;
    position: relative;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    background: #f5f5f5;
    padding: 4px;
  }

  .tab-item {
    flex: 1;
    min-width: 120px;
    position: relative;
  }

  .tab-button {
    width: 100%;
    min-height: 44px; /* Minimum height for consistency */
    padding: 12px 16px;
    background: #fff;
    color: ${COLORS.SECONDARY};
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-family: var(--font-family-base);
    font-weight: 500;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 1px;
    z-index: 1;
    white-space: normal; /* Allow text to wrap if needed */
    
    /* Efecto shine en hover */
    &:after {
      content: '';
      position: absolute;
      top: -50%;
      left: -60%;
      width: 20%;
      height: 200%;
      opacity: 0;
      transform: rotate(30deg);
      background: rgba(255, 255, 255, 0.13);
      background: linear-gradient(
        to right, 
        rgba(255, 255, 255, 0.13) 0%,
        rgba(255, 255, 255, 0.13) 77%,
        rgba(255, 255, 255, 0.5) 92%,
        rgba(255, 255, 255, 0.0) 100%
      );
      z-index: 2;
    }
    
    &:hover:not(.active) {
      color: #333;
      background: #fff;
      box-shadow: 0 3px 6px rgba(0, 0, 0, 0.08);
      z-index: 2;
      
      &:after {
        opacity: 1;
        left: 130%;
        transition: left 0.7s ease;
      }
    }
    
    &.active {
      background: ${COLORS.GRADIENT.PRIMARY};
      color: white;
      font-weight: 600;
      box-shadow: 0 4px 12px rgba(254, 190, 27, 0.3);
      z-index: 3;
      
      .tab-number {
        background: rgba(255, 255, 255, 0.2);
        color: white;
      }
    }
  }

  .tab-number {
    margin-right: 10px;
    font-weight: bold;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 24px;
    height: 24px;
    background: rgba(0, 0, 0, 0.05);
    border-radius: 50%;
    padding: 0 6px;
    font-size: 0.9em;
    transition: all 0.3s ease;
  }
`;

// Variant for table tabs
export const TableTabStyle = styled(TabStyle)`
  .horizontal-tabs-list {
    margin-bottom: 0;
    box-shadow: none;
    background: transparent;
    padding: 0;
    gap: 1px;
  }
  
  .tab-button {
    padding: 10px 16px;
    min-height: 40px; /* Slightly smaller minimum height for table tabs */
    font-size: 0.95em;
    border-radius: 6px 6px 0 0;
    margin-bottom: -1px;
    border-bottom: none;
    background: rgba(245, 245, 245, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    
    &.active {
      background: ${COLORS.GRADIENT.PRIMARY};
      color: white;
      box-shadow: 0 -2px 10px rgba(254, 190, 27, 0.2);
    }
    
    &:hover:not(.active) {
      background: rgba(254, 190, 27, 0.1);
    }
    
    .tab-number {
      min-width: 20px;
      height: 20px;
      font-size: 0.85em;
    }
  }
`;

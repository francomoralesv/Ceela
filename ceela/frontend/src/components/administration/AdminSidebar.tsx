import React from "react";

interface SidebarStep {
  stepNumber: number;
  iconName: string;
  title: string;
  route?: string;
}

interface SidebarItemProps {
  step: SidebarStep;
  activeStep: number;
  onStepChange: () => void;
}

const SidebarItem: React.FC<SidebarItemProps> = ({
  step,
  activeStep,
  onStepChange,
}) => {
  const primaryColor = "#3ca7b7";
  const inactiveColor = "#ccc";
  const isActive = activeStep === step.stepNumber;

  return (
    <>
      <li className="sidebar-item" onClick={onStepChange}>
        <div
          className={`sidebar-item-content d-flex align-items-center ${isActive ? "active" : ""}`}
          style={{
            height: "60px",
            border: `1px solid ${isActive ? primaryColor : inactiveColor}`,
            color: isActive ? primaryColor : inactiveColor,
            padding: "0 1rem",
          }}
        >
          <span className="icon-wrapper me-2">
            <span className="material-icons">{step.iconName}</span>
          </span>
          <span className="title-wrapper">{step.title}</span>
        </div>
      </li>
      <style jsx>{`
        .sidebar-item {
          list-style: none;
          margin: 10px 0;
          cursor: pointer;
          transition: background-color 0.3s ease;
        }
        .sidebar-item:hover {
          background-color: #f7f7f7;
        }
        .sidebar-item-content {
          border-radius: 4px;
          overflow: hidden;
          transition: transform 0.3s ease-out, box-shadow 0.3s ease-out;
        }
        .sidebar-item-content:hover {
          transform: translateX(8px);
          box-shadow: 0 4px 25px rgba(60, 167, 183, 0.1),
                      0 1px 5px rgba(0, 0, 0, 0.1);
        }
        .sidebar-item-content.active .icon-wrapper {
          border: 2px solid ${primaryColor};
          border-radius: 50%;
          padding: 5px;
          background: ${primaryColor};
          color: #fff;
        }
      `}</style>
    </>
  );
};

interface AdminSidebarProps {
  activeStep: number;
  onStepChange: (step: number) => void;
  steps: SidebarStep[];
  onClickAction?: (route: string) => void;
}

export const AdminSidebar: React.FC<AdminSidebarProps> = ({
  activeStep,
  onStepChange,
  steps,
  onClickAction,
}) => {
  const handleClick = (step: SidebarStep) => {
    if (onClickAction && step.route) {
      onClickAction(step.route);
    } else {
      onStepChange(step.stepNumber);
    }
  };

  return (
    <div className="internal-sidebar">
      <ul className="nav">
        {steps.map((step) => (
          <SidebarItem
            key={step.stepNumber}
            step={step}
            activeStep={activeStep}
            onStepChange={() => handleClick(step)}
          />
        ))}
      </ul>
      <style jsx>{`
        .internal-sidebar {
          width: 100%;
          max-width: 380px;
          margin: 0 auto;
        }
        .nav {
          list-style: none;
          padding: 0;
          margin: 0;
          display: flex;
          flex-direction: column;
        }
        /* En pantallas pequeñas, el sidebar se extiende al 100% y cada item ocupa toda la fila */
        @media (max-width: 768px) {
          .internal-sidebar {
            max-width: 100%;
            width: 100%;
          }
          .nav {
            width: 100%;
          }
          .sidebar-item-content {
            width: 100%;
            justify-content: flex-start;
          }
        }
      `}</style>
    </div>
  );
};

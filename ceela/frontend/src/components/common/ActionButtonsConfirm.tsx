import React from "react";
import CustomButton from "./CustomButton";

interface AcceptCancelButtonsProps {
  onAccept: () => void;
  onCancel: () => void;
}

const ActionButtonsConfirm: React.FC<AcceptCancelButtonsProps> = ({ onAccept, onCancel }) => {
  return (
    <div className="buttons-container">
      <CustomButton variant="save" className="btn-table-list" onClick={onAccept}>
        ✔
      </CustomButton>
      <CustomButton variant="closed" className="btn-table-list" onClick={onCancel}>
        ✖
      </CustomButton>
    </div>
  );
};

export default ActionButtonsConfirm;

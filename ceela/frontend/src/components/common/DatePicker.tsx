import React from 'react';

interface DatePickerProps {
  label: string;
  selectedDate: string;
  onChange: (date: string) => void;
}

const DatePicker: React.FC<DatePickerProps> = ({ label, selectedDate, onChange }) => {
  return (
    <div className="mb-3">
      <label className="form-label">{label}</label>
      <input
        type="date"
        value={selectedDate}
        onChange={(e) => onChange(e.target.value)}
        className="form-control"
      />
    </div>
  );
};

export default DatePicker;

import CustomButton from "@/components/common/CustomButton";
import { Detail } from "pages/workflow-part2-edit";

export const EditDetailMuroChild= ({
    onClick,
    disabled,
    detail
}: {
    onClick: (detail: Detail) => void;
    disabled: boolean;
    detail: Detail;
}) => {

    const handleEditDetail = (detail: Detail) => {
        console.log('Handle edit',detail)
        onClick(detail);
      };
    return (
        <CustomButton
            className="btn-table"
            variant="editIcon"
            onClick={() => handleEditDetail(detail)}
            disabled={
               disabled
            }
        >
            Editar
        </CustomButton>
    );
};

export default CustomButton;

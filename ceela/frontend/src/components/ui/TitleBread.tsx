import { useRouter } from 'next/router';
import React from 'react';
import Title from '../Title';
import Breadcrumb from '../common/Breadcrumb';
import Card from '../common/Card';
import CustomButton from '../common/CustomButton';

interface BreadcrumbItem {
    title: string;
    href: string;
    active?: boolean;
}

interface TitleBreadProps {
    title: string;
    breadcrumbItems: BreadcrumbItem[];
    showBackButton?: boolean;
    backButtonCallback?: () => void;
}

const TitleBread: React.FC<TitleBreadProps> = ({
    title,
    breadcrumbItems,
    showBackButton = false,
    backButtonCallback
}) => {
    const router = useRouter();

    const handleGoBack = () => {
        if (backButtonCallback) {
            backButtonCallback();
        } else {
            router.back();
        }
    };

    return (
        <Card>
            <div className="d-flex align-items-center justify-content-between w-100">

                {showBackButton && (
                    <CustomButton
                        variant="backIcon"
                        onClick={handleGoBack}
                    >
                        Volver
                    </CustomButton>
                )}
                <div className="d-flex align-items-center">
                    <Breadcrumb items={breadcrumbItems} />
                </div>
            </div>
        </Card>
    );
};

export default TitleBread;
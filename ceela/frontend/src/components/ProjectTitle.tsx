'use client'
import { useRouter } from 'next/router';
import Title from './Title';
import Breadcrumb from './common/Breadcrumb';
import Card from './common/Card';
import CustomButton from './common/CustomButton';

interface ProjectTitleProps {
    projectName?: string;
    region?: string;
}

const ProjectTitle: React.FC<ProjectTitleProps> = ({ projectName,region }) => {
    const router = useRouter();
    const titleText = (router.query.id ? "Edición de Proyecto" : "Proyecto nuevo")

    return (
        <>
            <Card>
                <div className="d-flex align-items-center w-100">
                    <Title text={titleText} />
                    <Breadcrumb
                        items={[
                            {
                                title: "Lista de proyectos",
                                href: "/project-list",
                                active: false,
                            },
                            {
                                title: router.query.id ? projectName || "Editar Proyecto" : "Nuevo proyecto",
                                href: "/",
                                active: true,
                            },
                        ]}
                    />
                </div>
            </Card>
            <Card>

                <div className="d-flex align-items-center gap-4">
                    <span style={{ fontWeight: "normal", fontFamily: "var(--font-family-base)" }}>
                        Proyecto:
                    </span>
                    <CustomButton
                        variant="save"
                        className="no-hover"
                        style={{ padding: "0.8rem 3rem" }}
                    >
                        {`${projectName ?? "xxxxx"}`}
                    </CustomButton>

                    <span style={{ fontWeight: "normal", fontFamily: "var(--font-family-base)" }}>
                        Región:
                    </span>
                    <CustomButton
                        variant="save"
                        className="no-hover"
                        style={{ padding: "0.8rem 3rem" }}
                    >
                        {region}
                    </CustomButton>
                </div>
            </Card>
        </>
    );
};

export default ProjectTitle;
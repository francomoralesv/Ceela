import TitleBread from "@/components/ui/TitleBread";
import dynamic from "next/dynamic";

const IFCViewerComponent = dynamic(() => import("@/components/ifc/Viewer"), { ssr: false });

export default function Home() {
  return (
    <div>
      <TitleBread 
        title="Gestor IFC" 
        breadcrumbItems={[{ title: "Gestor IFC", href: "/ifc" }]} 
        showBackButton={true}
      />
      <IFCViewerComponent />
    </div>
  );
}

export async function getServerSideProps() {
  return { props: {} };
}

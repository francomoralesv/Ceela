import { GetServerSideProps } from "next";
import "react-toastify/dist/ReactToastify.css";

export const getServerSideProps: GetServerSideProps = async () => {
  return {
    redirect: {
      destination: "/login",
      permanent: false,
    },
  };
}

export default function Home() {
  return null;
}

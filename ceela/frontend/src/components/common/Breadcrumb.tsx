import Link from "next/link";
import { useRouter } from "next/router";
import React from "react";

interface BreadcrumbItem {
  title: string;
  href?: string;
  active?: boolean;
}

interface BreadcrumbProps {
  items: BreadcrumbItem[];
}

const Breadcrumb: React.FC<BreadcrumbProps> = ({ items }) => {
  const router = useRouter();

  const handleHomeClick = () => {
    const roleId = localStorage.getItem("role_id");
    if (roleId === "1") {
      router.push("/dashboard");
    } else if (roleId === "2") {
      router.push("/project-list");
    }
  };

  return (
    <div className="breadcrumb-container row p-0 page-title m-4">
      <ol
        className="breadcrumb me-4"
        style={{ textDecoration: "none", color: "#2ab0c5" }}
      >
        <li className="breadcrumb-item">
          <a
            onClick={handleHomeClick}
            style={{
              textDecoration: "none",
              color: "#2ab0c5",
              cursor: "pointer",
              fontWeight: "bold"
            }}
          >
            <span className="material-icons" style={{ color: "#2ab0c5" }}>
              home
            </span>
          </a>
        </li>
        {items.map((item, index) => (
          <li
            key={index}
            className={`breadcrumb-item ${item.active ? "active" : ""}`}
          >
            {item.href ? (
              <Link
                href={item.href}
                style={{
                  textDecoration: "none",
                  color: "#2ab0c5",
                  fontWeight: "bold",
                  transition: "color 0.3s ease"
                }}
              >
                {item.title}
              </Link>
            ) : (
              <span style={{ color: "#2ab0c5", fontWeight: "bold" }}>{item.title}</span>
            )}
          </li>
        ))}
      </ol>
    </div>
  );
};

export default Breadcrumb;

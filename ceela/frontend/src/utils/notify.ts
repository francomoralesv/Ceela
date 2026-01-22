import Swal from "sweetalert2";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

export function notify(message: string, type: string = 'default', time = 2000) {
    if (type === "modal") {
        Swal.fire({
            title: message,
            icon: "info",
            showConfirmButton: true,
        });
    } else if (type === "error") {
        toast.error(message, { autoClose: time });
    } else if (type === "success") {
        toast.success(message, { autoClose: time });
    } else { // default case
        toast.info(message, { autoClose: time });
    }
}
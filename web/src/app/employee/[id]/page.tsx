"use client";

import { useParams, Navigate } from "react-router-dom";
import EmployeeDetail from "./client";

export default function EmployeeDetailPage() {
    const params = useParams();
    const employeeId = parseInt(params.id ?? "", 10);

    if (isNaN(employeeId)) {
        return <Navigate to="/employee" replace />;
    }

    return <EmployeeDetail employeeId={employeeId} />;
}

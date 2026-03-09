import { useEffect } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { useAuthStore } from "@/store/auth";
import { Layout } from "@/components/Layout";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { Login } from "@/pages/Login";
import { Dashboard } from "@/pages/Dashboard";
import { Timesheet } from "@/pages/timekeeping/Timesheet";
import { Documents } from "@/pages/documents/Documents";
import { Reports } from "@/pages/reports/Reports";
import { Users } from "@/pages/users/Users";
import { Departments } from "@/pages/users/Departments";
import { Audit } from "@/pages/audit/Audit";

export default function App() {
  const { fetchMe } = useAuthStore();

  useEffect(() => {
    if (localStorage.getItem("access_token")) {
      fetchMe();
    } else {
      useAuthStore.setState({ loading: false });
    }
  }, []);

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />

        <Route
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />

          {/* Timekeeping */}
          <Route
            path="/timesheet"
            element={
              <ProtectedRoute allowedRoles={["superadmin", "hr", "manager"]}>
                <Timesheet />
              </ProtectedRoute>
            }
          />
          <Route
            path="/timesheet/me"
            element={
              <ProtectedRoute allowedRoles={["employee", "superadmin", "hr", "manager"]}>
                <Timesheet />
              </ProtectedRoute>
            }
          />

          {/* Documents */}
          <Route path="/documents" element={
            <ProtectedRoute allowedRoles={["superadmin", "hr", "manager"]}>
              <Documents />
            </ProtectedRoute>
          } />
          <Route path="/documents/me" element={
            <ProtectedRoute>
              <Documents mine />
            </ProtectedRoute>
          } />

          {/* Reports */}
          <Route path="/reports" element={
            <ProtectedRoute allowedRoles={["superadmin", "hr", "manager"]}>
              <Reports />
            </ProtectedRoute>
          } />

          {/* Users */}
          <Route path="/users" element={
            <ProtectedRoute allowedRoles={["superadmin", "hr"]}>
              <Users />
            </ProtectedRoute>
          } />
          <Route path="/departments" element={
            <ProtectedRoute allowedRoles={["superadmin"]}>
              <Departments />
            </ProtectedRoute>
          } />

          {/* Audit */}
          <Route path="/audit" element={
            <ProtectedRoute allowedRoles={["superadmin"]}>
              <Audit />
            </ProtectedRoute>
          } />
        </Route>

        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

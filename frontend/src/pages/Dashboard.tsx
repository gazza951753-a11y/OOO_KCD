import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ClipboardList, FileText, BarChart3, Users } from "lucide-react";
import { useAuthStore } from "@/store/auth";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import api from "@/api/axios";

interface Stats {
  total_employees?: number;
  pending_documents?: number;
  timesheet_today?: number;
}

const ROLE_LABELS: Record<string, string> = {
  superadmin: "Суперадминистратор",
  hr: "Специалист по кадрам",
  manager: "Руководитель",
  employee: "Сотрудник",
};

export function Dashboard() {
  const { user } = useAuthStore();
  const [stats, setStats] = useState<Stats>({});

  useEffect(() => {
    // Fetch basic stats from available endpoints
    if (user?.role === "hr" || user?.role === "superadmin") {
      api.get("/users").then((r) => setStats((s) => ({ ...s, total_employees: r.data.length }))).catch(() => {});
      api.get("/documents").then((r) => {
        const pending = r.data.filter((d: { status: string }) => d.status === "pending").length;
        setStats((s) => ({ ...s, pending_documents: pending }));
      }).catch(() => {});
    }
  }, [user]);

  const today = new Date().toLocaleDateString("ru-RU", { weekday: "long", year: "numeric", month: "long", day: "numeric" });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Добро пожаловать, {user?.full_name?.split(" ")[1] ?? user?.full_name}!</h1>
        <p className="text-muted-foreground">{ROLE_LABELS[user?.role ?? "employee"]} · {today}</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {(user?.role === "hr" || user?.role === "superadmin") && (
          <>
            <Link to="/users">
              <Card className="hover:shadow-md transition-shadow cursor-pointer">
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium">Сотрудников</CardTitle>
                  <Users className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats.total_employees ?? "—"}</div>
                  <p className="text-xs text-muted-foreground">Всего в системе</p>
                </CardContent>
              </Card>
            </Link>

            <Link to="/documents">
              <Card className="hover:shadow-md transition-shadow cursor-pointer">
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium">Ожидают рассмотрения</CardTitle>
                  <FileText className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats.pending_documents ?? "—"}</div>
                  <p className="text-xs text-muted-foreground">Заявок на документы</p>
                </CardContent>
              </Card>
            </Link>
          </>
        )}

        {(user?.role === "hr" || user?.role === "manager" || user?.role === "superadmin") && (
          <Link to="/timesheet">
            <Card className="hover:shadow-md transition-shadow cursor-pointer">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Табельный учёт</CardTitle>
                <ClipboardList className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">→</div>
                <p className="text-xs text-muted-foreground">Перейти к табелю</p>
              </CardContent>
            </Card>
          </Link>
        )}

        {user?.role === "employee" && (
          <>
            <Link to="/timesheet/me">
              <Card className="hover:shadow-md transition-shadow cursor-pointer">
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium">Мой табель</CardTitle>
                  <ClipboardList className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">→</div>
                  <p className="text-xs text-muted-foreground">Просмотр и история</p>
                </CardContent>
              </Card>
            </Link>

            <Link to="/documents/me">
              <Card className="hover:shadow-md transition-shadow cursor-pointer">
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium">Мои заявки</CardTitle>
                  <FileText className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">→</div>
                  <p className="text-xs text-muted-foreground">Документы и статусы</p>
                </CardContent>
              </Card>
            </Link>
          </>
        )}

        {(user?.role === "hr" || user?.role === "manager" || user?.role === "superadmin") && (
          <Link to="/reports">
            <Card className="hover:shadow-md transition-shadow cursor-pointer">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Отчёты</CardTitle>
                <BarChart3 className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">Excel / PDF</div>
                <p className="text-xs text-muted-foreground">Генерация отчётов</p>
              </CardContent>
            </Card>
          </Link>
        )}
      </div>
    </div>
  );
}

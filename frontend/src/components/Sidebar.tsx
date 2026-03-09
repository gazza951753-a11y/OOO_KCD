import { Link, useLocation } from "react-router-dom";
import {
  BarChart3,
  Building2,
  ClipboardList,
  FileText,
  Home,
  LogOut,
  ScrollText,
  Users,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/store/auth";
import { Button } from "./ui/button";

const ROLE_LABELS: Record<string, string> = {
  superadmin: "Суперадмин",
  hr: "Кадровик",
  manager: "Руководитель",
  employee: "Сотрудник",
};

interface NavItem {
  label: string;
  href: string;
  icon: React.ReactNode;
  roles: string[];
}

const navItems: NavItem[] = [
  { label: "Главная", href: "/dashboard", icon: <Home className="h-4 w-4" />, roles: ["superadmin", "hr", "manager", "employee"] },
  { label: "Табельный учёт", href: "/timesheet", icon: <ClipboardList className="h-4 w-4" />, roles: ["hr", "manager"] },
  { label: "Мой табель", href: "/timesheet/me", icon: <ClipboardList className="h-4 w-4" />, roles: ["employee"] },
  { label: "Документооборот", href: "/documents", icon: <FileText className="h-4 w-4" />, roles: ["hr", "manager"] },
  { label: "Мои документы", href: "/documents/me", icon: <FileText className="h-4 w-4" />, roles: ["employee"] },
  { label: "Отчёты", href: "/reports", icon: <BarChart3 className="h-4 w-4" />, roles: ["superadmin", "hr", "manager"] },
  { label: "Сотрудники", href: "/users", icon: <Users className="h-4 w-4" />, roles: ["superadmin", "hr"] },
  { label: "Отделы", href: "/departments", icon: <Building2 className="h-4 w-4" />, roles: ["superadmin"] },
  { label: "Аудит", href: "/audit", icon: <ScrollText className="h-4 w-4" />, roles: ["superadmin"] },
];

export function Sidebar() {
  const location = useLocation();
  const { user, logout } = useAuthStore();

  const visible = navItems.filter((item) => user && item.roles.includes(user.role));

  return (
    <aside className="flex h-screen w-60 flex-col border-r bg-background">
      <div className="border-b px-6 py-4">
        <div className="text-lg font-bold text-primary">ООО КЦД</div>
        <div className="text-xs text-muted-foreground">Кадровая система</div>
      </div>

      <nav className="flex-1 overflow-auto py-4">
        <ul className="space-y-1 px-3">
          {visible.map((item) => (
            <li key={item.href}>
              <Link
                to={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground",
                  location.pathname === item.href && "bg-accent text-accent-foreground"
                )}
              >
                {item.icon}
                {item.label}
              </Link>
            </li>
          ))}
        </ul>
      </nav>

      <div className="border-t p-4">
        <div className="mb-3 rounded-md bg-muted px-3 py-2">
          <div className="text-sm font-medium truncate">{user?.full_name}</div>
          <div className="text-xs text-muted-foreground">{user ? ROLE_LABELS[user.role] : ""}</div>
        </div>
        <Button variant="outline" size="sm" className="w-full gap-2" onClick={logout}>
          <LogOut className="h-4 w-4" />
          Выйти
        </Button>
      </div>
    </aside>
  );
}

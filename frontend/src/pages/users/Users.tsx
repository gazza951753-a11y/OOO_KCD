import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Plus, UserX } from "lucide-react";
import api from "@/api/axios";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

const ROLE_LABELS: Record<string, string> = {
  superadmin: "Суперадмин",
  hr: "Кадровик",
  manager: "Руководитель",
  employee: "Сотрудник",
};

interface User {
  id: number;
  email: string;
  full_name: string;
  role: string;
  position: string | null;
  is_active: boolean;
  department?: { name: string } | null;
}

interface Department { id: number; name: string }

const schema = z.object({
  email: z.string().email("Введите корректный email"),
  full_name: z.string().min(2, "Введите ФИО"),
  password: z.string().min(8, "Минимум 8 символов"),
  role: z.string().min(1, "Выберите роль"),
  position: z.string().optional(),
  department_id: z.string().optional(),
});
type FormData = z.infer<typeof schema>;

export function Users() {
  const [users, setUsers] = useState<User[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [open, setOpen] = useState(false);

  const { register, handleSubmit, setValue, reset, formState: { errors, isSubmitting } } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const load = () => {
    api.get("/users").then((r) => setUsers(r.data)).catch(console.error);
    api.get("/departments").then((r) => setDepartments(r.data)).catch(console.error);
  };

  useEffect(() => { load(); }, []);

  const onSubmit = async (data: FormData) => {
    await api.post("/users", {
      ...data,
      department_id: data.department_id ? parseInt(data.department_id) : null,
    });
    setOpen(false);
    reset();
    load();
  };

  const deactivate = async (id: number) => {
    if (!confirm("Деактивировать пользователя?")) return;
    await api.delete(`/users/${id}`);
    load();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Сотрудники</h1>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button className="gap-2"><Plus className="h-4 w-4" />Добавить</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Новый пользователь</DialogTitle></DialogHeader>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-3">
              <div className="space-y-1">
                <Label>ФИО</Label>
                <Input {...register("full_name")} placeholder="Иванов Иван Иванович" />
                {errors.full_name && <p className="text-xs text-destructive">{errors.full_name.message}</p>}
              </div>
              <div className="space-y-1">
                <Label>Email</Label>
                <Input type="email" {...register("email")} placeholder="user@kcd.ru" />
                {errors.email && <p className="text-xs text-destructive">{errors.email.message}</p>}
              </div>
              <div className="space-y-1">
                <Label>Пароль</Label>
                <Input type="password" {...register("password")} placeholder="Минимум 8 символов" />
                {errors.password && <p className="text-xs text-destructive">{errors.password.message}</p>}
              </div>
              <div className="space-y-1">
                <Label>Роль</Label>
                <Select onValueChange={(v) => setValue("role", v)}>
                  <SelectTrigger><SelectValue placeholder="Выберите роль" /></SelectTrigger>
                  <SelectContent>
                    {Object.entries(ROLE_LABELS).map(([v, l]) => (
                      <SelectItem key={v} value={v}>{l}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {errors.role && <p className="text-xs text-destructive">{errors.role.message}</p>}
              </div>
              <div className="space-y-1">
                <Label>Отдел</Label>
                <Select onValueChange={(v) => setValue("department_id", v)}>
                  <SelectTrigger><SelectValue placeholder="Без отдела" /></SelectTrigger>
                  <SelectContent>
                    {departments.map((d) => (
                      <SelectItem key={d.id} value={String(d.id)}>{d.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-1">
                <Label>Должность</Label>
                <Input {...register("position")} placeholder="Необязательно" />
              </div>
              <Button type="submit" className="w-full" disabled={isSubmitting}>
                {isSubmitting ? "Создание..." : "Создать"}
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardHeader><CardTitle className="text-base">Список сотрудников</CardTitle></CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-muted-foreground">
                  <th className="text-left py-2 pr-4">ФИО</th>
                  <th className="text-left py-2 pr-4">Email</th>
                  <th className="text-left py-2 pr-4">Роль</th>
                  <th className="text-left py-2 pr-4">Отдел</th>
                  <th className="text-left py-2 pr-4">Должность</th>
                  <th className="text-left py-2 pr-4">Статус</th>
                  <th className="text-left py-2">Действия</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id} className="border-b hover:bg-muted/30">
                    <td className="py-2 pr-4 font-medium">{u.full_name}</td>
                    <td className="py-2 pr-4 text-muted-foreground">{u.email}</td>
                    <td className="py-2 pr-4"><Badge variant="secondary">{ROLE_LABELS[u.role] ?? u.role}</Badge></td>
                    <td className="py-2 pr-4">{u.department?.name ?? "—"}</td>
                    <td className="py-2 pr-4">{u.position ?? "—"}</td>
                    <td className="py-2 pr-4">
                      {u.is_active
                        ? <Badge variant="success">Активен</Badge>
                        : <Badge variant="destructive">Деактивирован</Badge>
                      }
                    </td>
                    <td className="py-2">
                      {u.is_active && (
                        <Button size="sm" variant="ghost" onClick={() => deactivate(u.id)}>
                          <UserX className="h-4 w-4 text-destructive" />
                        </Button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { CheckCircle2, Plus } from "lucide-react";
import api from "@/api/axios";
import { useAuthStore } from "@/store/auth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { formatDate } from "@/lib/utils";

const STATUS_LABELS: Record<string, string> = {
  present: "Присутствие",
  absent: "Отсутствие",
  vacation: "Отпуск",
  sick: "Больничный",
  holiday: "Праздник",
  business_trip: "Командировка",
};

const STATUS_VARIANTS: Record<string, "default" | "success" | "destructive" | "warning" | "secondary"> = {
  present: "success",
  absent: "destructive",
  vacation: "secondary",
  sick: "warning",
  holiday: "secondary",
  business_trip: "default",
};

interface Record {
  id: number;
  user_id: number;
  date: string;
  check_in: string | null;
  check_out: string | null;
  status: string;
  work_hours: number | null;
  comment: string | null;
  approved_by: number | null;
  user?: { full_name: string };
}

interface User {
  id: number;
  full_name: string;
}

const createSchema = z.object({
  user_id: z.string().min(1, "Выберите сотрудника"),
  date: z.string().min(1, "Укажите дату"),
  check_in: z.string().optional(),
  check_out: z.string().optional(),
  status: z.string().min(1, "Выберите статус"),
  comment: z.string().optional(),
});
type CreateForm = z.infer<typeof createSchema>;

export function Timesheet() {
  const { user } = useAuthStore();
  const [records, setRecords] = useState<Record[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [open, setOpen] = useState(false);
  const isHR = user?.role === "hr" || user?.role === "superadmin";

  const { register, handleSubmit, setValue, reset, formState: { errors, isSubmitting } } = useForm<CreateForm>({
    resolver: zodResolver(createSchema),
    defaultValues: { status: "present" },
  });

  const load = () => {
    const endpoint = user?.role === "employee" ? "/timesheet/me" : "/timesheet";
    api.get(endpoint).then((r) => setRecords(r.data)).catch(console.error);
  };

  useEffect(() => {
    load();
    if (isHR) {
      api.get("/users").then((r) => setUsers(r.data)).catch(console.error);
    }
  }, []);

  const onSubmit = async (data: CreateForm) => {
    await api.post("/timesheet", {
      user_id: parseInt(data.user_id),
      date: data.date,
      check_in: data.check_in || null,
      check_out: data.check_out || null,
      status: data.status,
      comment: data.comment || null,
    });
    setOpen(false);
    reset();
    load();
  };

  const approve = async (id: number) => {
    await api.post(`/timesheet/${id}/approve`);
    load();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Табельный учёт</h1>
        {isHR && (
          <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
              <Button className="gap-2"><Plus className="h-4 w-4" />Добавить запись</Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader><DialogTitle>Новая запись табеля</DialogTitle></DialogHeader>
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                <div className="space-y-1">
                  <Label>Сотрудник</Label>
                  <Select onValueChange={(v) => setValue("user_id", v)}>
                    <SelectTrigger><SelectValue placeholder="Выберите сотрудника" /></SelectTrigger>
                    <SelectContent>
                      {users.map((u) => <SelectItem key={u.id} value={String(u.id)}>{u.full_name}</SelectItem>)}
                    </SelectContent>
                  </Select>
                  {errors.user_id && <p className="text-xs text-destructive">{errors.user_id.message}</p>}
                </div>
                <div className="space-y-1">
                  <Label>Дата</Label>
                  <Input type="date" {...register("date")} />
                  {errors.date && <p className="text-xs text-destructive">{errors.date.message}</p>}
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <Label>Приход</Label>
                    <Input type="time" {...register("check_in")} />
                  </div>
                  <div className="space-y-1">
                    <Label>Уход</Label>
                    <Input type="time" {...register("check_out")} />
                  </div>
                </div>
                <div className="space-y-1">
                  <Label>Статус</Label>
                  <Select defaultValue="present" onValueChange={(v) => setValue("status", v)}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      {Object.entries(STATUS_LABELS).map(([v, l]) => (
                        <SelectItem key={v} value={v}>{l}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-1">
                  <Label>Комментарий</Label>
                  <Input {...register("comment")} placeholder="Необязательно" />
                </div>
                <Button type="submit" className="w-full" disabled={isSubmitting}>
                  {isSubmitting ? "Сохранение..." : "Сохранить"}
                </Button>
              </form>
            </DialogContent>
          </Dialog>
        )}
      </div>

      <Card>
        <CardHeader><CardTitle className="text-base">Записи</CardTitle></CardHeader>
        <CardContent>
          {records.length === 0 ? (
            <p className="text-center text-muted-foreground py-8">Нет записей</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-muted-foreground">
                    {!["employee"].includes(user?.role ?? "") && <th className="text-left py-2 pr-4">Сотрудник</th>}
                    <th className="text-left py-2 pr-4">Дата</th>
                    <th className="text-left py-2 pr-4">Приход</th>
                    <th className="text-left py-2 pr-4">Уход</th>
                    <th className="text-left py-2 pr-4">Статус</th>
                    <th className="text-left py-2 pr-4">Часов</th>
                    <th className="text-left py-2 pr-4">Утверждён</th>
                    {(isHR || user?.role === "manager") && <th className="text-left py-2">Действия</th>}
                  </tr>
                </thead>
                <tbody>
                  {records.map((rec) => (
                    <tr key={rec.id} className="border-b hover:bg-muted/30">
                      {!["employee"].includes(user?.role ?? "") && (
                        <td className="py-2 pr-4 font-medium">{rec.user?.full_name ?? rec.user_id}</td>
                      )}
                      <td className="py-2 pr-4">{formatDate(rec.date)}</td>
                      <td className="py-2 pr-4">{rec.check_in ?? "—"}</td>
                      <td className="py-2 pr-4">{rec.check_out ?? "—"}</td>
                      <td className="py-2 pr-4">
                        <Badge variant={STATUS_VARIANTS[rec.status] ?? "default"}>
                          {STATUS_LABELS[rec.status] ?? rec.status}
                        </Badge>
                      </td>
                      <td className="py-2 pr-4">{rec.work_hours ?? "—"}</td>
                      <td className="py-2 pr-4">
                        {rec.approved_by ? <CheckCircle2 className="h-4 w-4 text-green-500" /> : "—"}
                      </td>
                      {(isHR || user?.role === "manager") && (
                        <td className="py-2">
                          {!rec.approved_by && (
                            <Button size="sm" variant="outline" onClick={() => approve(rec.id)}>
                              Утвердить
                            </Button>
                          )}
                        </td>
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

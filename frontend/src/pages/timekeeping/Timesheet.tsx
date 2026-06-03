import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { AlertTriangle, CheckCircle2, Plus } from "lucide-react";
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

// Statuses that require a supporting document
const REQUIRES_DOC = new Set(["absent", "vacation", "sick", "business_trip"]);

interface TimesheetRecord {
  id: number;
  user_id: number;
  date: string;
  check_in: string | null;
  check_out: string | null;
  status: string;
  work_hours: number | null;
  comment: string | null;
  approved_by: number | null;
  document_id: number | null;
  requires_document: boolean;
  user?: { full_name: string };
}

interface UserItem {
  id: number;
  full_name: string;
}

interface DocItem {
  id: number;
  title: string;
  type: string;
  requester_id: number;
}

const createSchema = z
  .object({
    user_id: z.string().min(1, "Выберите сотрудника"),
    date: z.string().min(1, "Укажите дату"),
    check_in: z.string().optional(),
    check_out: z.string().optional(),
    status: z.string().min(1, "Выберите статус"),
    comment: z.string().optional(),
    document_id: z.string().optional(),
  })
  .superRefine((d, ctx) => {
    if (REQUIRES_DOC.has(d.status) && !d.document_id) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "Для данного статуса необходим документ-основание",
        path: ["document_id"],
      });
    }
  });

type CreateForm = z.infer<typeof createSchema>;

export function Timesheet() {
  const { user } = useAuthStore();
  const [records, setRecords] = useState<TimesheetRecord[]>([]);
  const [users, setUsers] = useState<UserItem[]>([]);
  const [documents, setDocuments] = useState<DocItem[]>([]);
  const [open, setOpen] = useState(false);
  const [selectedStatus, setSelectedStatus] = useState("present");
  const [selectedUserId, setSelectedUserId] = useState("");
  const isHR = user?.role === "hr" || user?.role === "superadmin";

  const {
    register, handleSubmit, setValue, reset,
    formState: { errors, isSubmitting },
  } = useForm<CreateForm>({
    resolver: zodResolver(createSchema),
    defaultValues: { status: "present" },
  });

  const load = () => {
    const endpoint = user?.role === "employee" ? "/timesheet/me" : "/timesheet";
    api.get<TimesheetRecord[]>(endpoint).then((r) => setRecords(r.data)).catch(console.error);
  };

  useEffect(() => {
    load();
    if (isHR) {
      api.get<UserItem[]>("/users").then((r) => setUsers(r.data)).catch(console.error);
      api.get<DocItem[]>("/documents").then((r) => setDocuments(r.data)).catch(console.error);
    }
  }, []);

  // Documents filtered by the selected employee
  const filteredDocs = selectedUserId
    ? documents.filter((d) => d.requester_id === parseInt(selectedUserId))
    : documents;

  const needsDoc = REQUIRES_DOC.has(selectedStatus);

  const onSubmit = async (data: CreateForm) => {
    await api.post("/timesheet", {
      user_id: parseInt(data.user_id),
      date: data.date,
      check_in: data.check_in || null,
      check_out: data.check_out || null,
      status: data.status,
      comment: data.comment || null,
      document_id: data.document_id ? parseInt(data.document_id) : null,
    });
    setOpen(false);
    reset();
    setSelectedStatus("present");
    setSelectedUserId("");
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
              <Button className="gap-2">
                <Plus className="h-4 w-4" />
                Добавить запись
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Новая запись табеля</DialogTitle>
              </DialogHeader>
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                {/* Employee */}
                <div className="space-y-1">
                  <Label>Сотрудник</Label>
                  <Select
                    onValueChange={(v) => {
                      setValue("user_id", v);
                      setSelectedUserId(v);
                      setValue("document_id", "");
                    }}
                  >
                    <SelectTrigger><SelectValue placeholder="Выберите сотрудника" /></SelectTrigger>
                    <SelectContent>
                      {users.map((u) => (
                        <SelectItem key={u.id} value={String(u.id)}>{u.full_name}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {errors.user_id && <p className="text-xs text-destructive">{errors.user_id.message}</p>}
                </div>

                {/* Date */}
                <div className="space-y-1">
                  <Label>Дата</Label>
                  <Input type="date" {...register("date")} />
                  {errors.date && <p className="text-xs text-destructive">{errors.date.message}</p>}
                </div>

                {/* Check-in / Check-out */}
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

                {/* Status */}
                <div className="space-y-1">
                  <Label>Статус</Label>
                  <Select
                    defaultValue="present"
                    onValueChange={(v) => {
                      setValue("status", v);
                      setSelectedStatus(v);
                      if (!REQUIRES_DOC.has(v)) setValue("document_id", "");
                    }}
                  >
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      {Object.entries(STATUS_LABELS).map(([v, l]) => (
                        <SelectItem key={v} value={v}>{l}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Document selector — shown only when status requires it */}
                {needsDoc && (
                  <div className="space-y-1">
                    <div className="flex items-center gap-1.5 text-xs text-amber-700 mb-1">
                      <AlertTriangle className="h-3.5 w-3.5" />
                      Для этого статуса требуется документ-основание
                    </div>
                    <Label>Документ-основание</Label>
                    <Select onValueChange={(v) => setValue("document_id", v)}>
                      <SelectTrigger>
                        <SelectValue placeholder="Выберите документ" />
                      </SelectTrigger>
                      <SelectContent>
                        {filteredDocs.length === 0 ? (
                          <SelectItem value="" disabled>
                            Нет доступных документов
                          </SelectItem>
                        ) : (
                          filteredDocs.map((d) => (
                            <SelectItem key={d.id} value={String(d.id)}>
                              #{d.id} {d.title}
                            </SelectItem>
                          ))
                        )}
                      </SelectContent>
                    </Select>
                    {errors.document_id && (
                      <p className="text-xs text-destructive">{errors.document_id.message}</p>
                    )}
                  </div>
                )}

                {/* Comment */}
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
            <p className="py-8 text-center text-muted-foreground">Нет записей</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-muted-foreground">
                    {user?.role !== "employee" && <th className="py-2 pr-4 text-left">Сотрудник</th>}
                    <th className="py-2 pr-4 text-left">Дата</th>
                    <th className="py-2 pr-4 text-left">Приход</th>
                    <th className="py-2 pr-4 text-left">Уход</th>
                    <th className="py-2 pr-4 text-left">Статус</th>
                    <th className="py-2 pr-4 text-left">Часов</th>
                    <th className="py-2 pr-4 text-left">Документ</th>
                    <th className="py-2 pr-4 text-left">Утверждён</th>
                    {(isHR || user?.role === "manager") && (
                      <th className="py-2 text-left">Действия</th>
                    )}
                  </tr>
                </thead>
                <tbody>
                  {records.map((rec) => (
                    <tr key={rec.id} className="border-b hover:bg-muted/30">
                      {user?.role !== "employee" && (
                        <td className="py-2 pr-4 font-medium">
                          {rec.user?.full_name ?? rec.user_id}
                        </td>
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
                        {rec.requires_document ? (
                          rec.document_id ? (
                            <span className="text-xs text-green-700">#{rec.document_id}</span>
                          ) : (
                            <span className="flex items-center gap-1 text-xs text-amber-600">
                              <AlertTriangle className="h-3 w-3" />нет
                            </span>
                          )
                        ) : (
                          "—"
                        )}
                      </td>
                      <td className="py-2 pr-4">
                        {rec.approved_by
                          ? <CheckCircle2 className="h-4 w-4 text-green-500" />
                          : "—"}
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

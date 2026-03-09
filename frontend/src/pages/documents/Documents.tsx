import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Plus } from "lucide-react";
import api from "@/api/axios";
import { useAuthStore } from "@/store/auth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { formatDateTime } from "@/lib/utils";

const TYPE_LABELS: Record<string, string> = {
  vacation_request: "Заявление на отпуск",
  sick_leave: "Больничный",
  reference: "Справка",
  other: "Другое",
};

const STATUS_LABELS: Record<string, string> = {
  draft: "Черновик",
  pending: "На рассмотрении",
  approved: "Одобрено",
  rejected: "Отклонено",
  completed: "Завершено",
};

const STATUS_VARIANTS: Record<string, "default" | "success" | "destructive" | "warning" | "secondary"> = {
  draft: "secondary",
  pending: "warning",
  approved: "success",
  rejected: "destructive",
  completed: "default",
};

interface Doc {
  id: number;
  type: string;
  title: string;
  description: string | null;
  status: string;
  created_at: string;
  requester?: { full_name: string };
  approver?: { full_name: string } | null;
  rejection_reason?: string | null;
}

const createSchema = z.object({
  type: z.string().min(1, "Выберите тип"),
  title: z.string().min(2, "Укажите заголовок"),
  description: z.string().optional(),
});
type CreateForm = z.infer<typeof createSchema>;

const rejectSchema = z.object({ rejection_reason: z.string().min(2, "Укажите причину") });
type RejectForm = z.infer<typeof rejectSchema>;

interface Props {
  mine?: boolean;
}

export function Documents({ mine = false }: Props) {
  const { user } = useAuthStore();
  const [docs, setDocs] = useState<Doc[]>([]);
  const [open, setOpen] = useState(false);
  const [rejectId, setRejectId] = useState<number | null>(null);

  const canApprove = user?.role === "manager" || user?.role === "hr" || user?.role === "superadmin";

  const { register, handleSubmit, setValue, reset, formState: { errors, isSubmitting } } = useForm<CreateForm>({
    resolver: zodResolver(createSchema),
  });

  const { register: rjReg, handleSubmit: rjSubmit, reset: rjReset, formState: { isSubmitting: rjSubmitting } } = useForm<RejectForm>({
    resolver: zodResolver(rejectSchema),
  });

  const load = () => {
    const endpoint = mine ? "/documents/me" : "/documents";
    api.get(endpoint).then((r) => setDocs(r.data)).catch(console.error);
  };

  useEffect(() => { load(); }, [mine]);

  const onCreate = async (data: CreateForm) => {
    await api.post("/documents", data);
    setOpen(false);
    reset();
    load();
  };

  const onApprove = async (id: number) => {
    await api.put(`/documents/${id}/approve`);
    load();
  };

  const onReject = async (data: RejectForm) => {
    if (!rejectId) return;
    await api.put(`/documents/${rejectId}/reject`, data);
    setRejectId(null);
    rjReset();
    load();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">{mine ? "Мои документы" : "Документооборот"}</h1>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button className="gap-2"><Plus className="h-4 w-4" />Новая заявка</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Создать заявку</DialogTitle></DialogHeader>
            <form onSubmit={handleSubmit(onCreate)} className="space-y-4">
              <div className="space-y-1">
                <Label>Тип документа</Label>
                <Select onValueChange={(v) => setValue("type", v)}>
                  <SelectTrigger><SelectValue placeholder="Выберите тип" /></SelectTrigger>
                  <SelectContent>
                    {Object.entries(TYPE_LABELS).map(([v, l]) => (
                      <SelectItem key={v} value={v}>{l}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {errors.type && <p className="text-xs text-destructive">{errors.type.message}</p>}
              </div>
              <div className="space-y-1">
                <Label>Заголовок</Label>
                <Input {...register("title")} placeholder="Краткое описание" />
                {errors.title && <p className="text-xs text-destructive">{errors.title.message}</p>}
              </div>
              <div className="space-y-1">
                <Label>Описание</Label>
                <Textarea {...register("description")} placeholder="Подробности (необязательно)" />
              </div>
              <Button type="submit" className="w-full" disabled={isSubmitting}>
                {isSubmitting ? "Отправка..." : "Отправить"}
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Reject dialog */}
      <Dialog open={rejectId !== null} onOpenChange={(o) => !o && setRejectId(null)}>
        <DialogContent>
          <DialogHeader><DialogTitle>Отклонить заявку</DialogTitle></DialogHeader>
          <form onSubmit={rjSubmit(onReject)} className="space-y-4">
            <div className="space-y-1">
              <Label>Причина отказа</Label>
              <Textarea {...rjReg("rejection_reason")} placeholder="Укажите причину" />
            </div>
            <Button type="submit" variant="destructive" className="w-full" disabled={rjSubmitting}>
              Отклонить
            </Button>
          </form>
        </DialogContent>
      </Dialog>

      <Card>
        <CardHeader><CardTitle className="text-base">Заявки</CardTitle></CardHeader>
        <CardContent>
          {docs.length === 0 ? (
            <p className="text-center text-muted-foreground py-8">Нет заявок</p>
          ) : (
            <div className="space-y-3">
              {docs.map((doc) => (
                <div key={doc.id} className="rounded-lg border p-4 space-y-2">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="font-medium">{doc.title}</div>
                      <div className="text-sm text-muted-foreground">
                        {TYPE_LABELS[doc.type] ?? doc.type}
                        {doc.requester && ` · ${doc.requester.full_name}`}
                        {` · ${formatDateTime(doc.created_at)}`}
                      </div>
                      {doc.description && <div className="text-sm mt-1">{doc.description}</div>}
                      {doc.rejection_reason && (
                        <div className="text-sm text-destructive mt-1">Причина отказа: {doc.rejection_reason}</div>
                      )}
                    </div>
                    <Badge variant={STATUS_VARIANTS[doc.status] ?? "default"}>
                      {STATUS_LABELS[doc.status] ?? doc.status}
                    </Badge>
                  </div>
                  {canApprove && doc.status === "pending" && (
                    <div className="flex gap-2 pt-1">
                      <Button size="sm" onClick={() => onApprove(doc.id)}>Одобрить</Button>
                      <Button size="sm" variant="destructive" onClick={() => setRejectId(doc.id)}>Отклонить</Button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

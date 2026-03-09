import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Plus } from "lucide-react";
import api from "@/api/axios";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";

interface Department { id: number; name: string; manager_id: number | null; manager?: { full_name: string } | null }

const schema = z.object({ name: z.string().min(2, "Введите название отдела") });
type FormData = z.infer<typeof schema>;

export function Departments() {
  const [departments, setDepartments] = useState<Department[]>([]);
  const [open, setOpen] = useState(false);

  const { register, handleSubmit, reset, formState: { errors, isSubmitting } } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const load = () => {
    api.get("/departments").then((r) => setDepartments(r.data)).catch(console.error);
  };

  useEffect(() => { load(); }, []);

  const onSubmit = async (data: FormData) => {
    await api.post("/departments", data);
    setOpen(false);
    reset();
    load();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Отделы</h1>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button className="gap-2"><Plus className="h-4 w-4" />Добавить</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Новый отдел</DialogTitle></DialogHeader>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div className="space-y-1">
                <Label>Название</Label>
                <Input {...register("name")} placeholder="Например: ИТ-отдел" />
                {errors.name && <p className="text-xs text-destructive">{errors.name.message}</p>}
              </div>
              <Button type="submit" className="w-full" disabled={isSubmitting}>
                {isSubmitting ? "Создание..." : "Создать"}
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardHeader><CardTitle className="text-base">Список отделов</CardTitle></CardHeader>
        <CardContent>
          {departments.length === 0 ? (
            <p className="text-center text-muted-foreground py-8">Нет отделов</p>
          ) : (
            <div className="space-y-2">
              {departments.map((d) => (
                <div key={d.id} className="flex items-center justify-between rounded-lg border px-4 py-3">
                  <div>
                    <div className="font-medium">{d.name}</div>
                    <div className="text-sm text-muted-foreground">
                      Руководитель: {d.manager?.full_name ?? "не назначен"}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

import { useEffect, useState } from "react";
import { AlertTriangle, Lock, Unlock } from "lucide-react";
import api from "@/api/axios";
import { useAuthStore } from "@/store/auth";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface Period {
  id: number;
  year: number;
  month: number;
  is_closed: boolean;
  closed_at: string | null;
  closed_by: number | null;
}

const MONTH_NAMES = [
  "", "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
  "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь",
];

export function Periods() {
  const { user } = useAuthStore();
  const [periods, setPeriods] = useState<Period[]>([]);
  const [loading, setLoading] = useState(false);
  const isSuperadmin = user?.role === "superadmin";

  const load = () =>
    api.get<Period[]>("/periods")
      .then((r) => setPeriods(r.data))
      .catch(console.error);

  useEffect(() => { load(); }, []);

  const toggle = async (p: Period) => {
    setLoading(true);
    try {
      const action = p.is_closed ? "open" : "close";
      await api.post(`/periods/${p.year}/${p.month}/${action}`);
      load();
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const hasClosed = periods.some((p) => p.is_closed);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Периоды учёта</h1>

      {hasClosed && (
        <div className="flex items-center gap-2 rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          <AlertTriangle className="h-4 w-4 shrink-0" />
          Закрытые периоды не допускают изменений в табеле
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Табельные периоды</CardTitle>
        </CardHeader>
        <CardContent>
          {periods.length === 0 ? (
            <p className="py-8 text-center text-muted-foreground">
              Периоды не созданы. Закройте первый период чтобы зафиксировать данные.
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-muted-foreground">
                    <th className="py-2 pr-4 text-left">Период</th>
                    <th className="py-2 pr-4 text-left">Статус</th>
                    <th className="py-2 pr-4 text-left">Дата закрытия</th>
                    <th className="py-2 text-left">Действие</th>
                  </tr>
                </thead>
                <tbody>
                  {periods.map((p) => (
                    <tr key={p.id} className="border-b hover:bg-muted/30">
                      <td className="py-2 pr-4 font-medium">
                        {MONTH_NAMES[p.month]} {p.year}
                      </td>
                      <td className="py-2 pr-4">
                        <Badge variant={p.is_closed ? "destructive" : "success"}>
                          {p.is_closed ? "Закрыт" : "Открыт"}
                        </Badge>
                      </td>
                      <td className="py-2 pr-4 text-muted-foreground">
                        {p.closed_at
                          ? new Date(p.closed_at).toLocaleDateString("ru-RU")
                          : "—"}
                      </td>
                      <td className="py-2">
                        {!p.is_closed && (
                          <Button
                            size="sm"
                            variant="outline"
                            disabled={loading}
                            onClick={() => toggle(p)}
                            className="gap-1"
                          >
                            <Lock className="h-3 w-3" />
                            Закрыть
                          </Button>
                        )}
                        {p.is_closed && isSuperadmin && (
                          <Button
                            size="sm"
                            variant="outline"
                            disabled={loading}
                            onClick={() => toggle(p)}
                            className="gap-1"
                          >
                            <Unlock className="h-3 w-3" />
                            Открыть
                          </Button>
                        )}
                        {p.is_closed && !isSuperadmin && (
                          <span className="text-xs text-muted-foreground">Только суперадмин</span>
                        )}
                      </td>
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

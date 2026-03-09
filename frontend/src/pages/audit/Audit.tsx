import { useEffect, useState } from "react";
import api from "@/api/axios";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatDateTime } from "@/lib/utils";

interface AuditEntry {
  id: number;
  user_id: number | null;
  action: string;
  entity_type: string;
  entity_id: number | null;
  old_data: Record<string, unknown> | null;
  new_data: Record<string, unknown> | null;
  ip_address: string | null;
  created_at: string;
}

const ACTION_VARIANTS: Record<string, "default" | "success" | "destructive" | "warning" | "secondary"> = {
  create: "success",
  update: "warning",
  delete: "destructive",
  deactivate: "destructive",
  approve: "success",
  reject: "destructive",
  login: "default",
};

export function Audit() {
  const [logs, setLogs] = useState<AuditEntry[]>([]);

  useEffect(() => {
    api.get("/audit?limit=200").then((r) => setLogs(r.data)).catch(console.error);
  }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Журнал аудита</h1>

      <Card>
        <CardHeader><CardTitle className="text-base">Последние события</CardTitle></CardHeader>
        <CardContent>
          {logs.length === 0 ? (
            <p className="text-center text-muted-foreground py-8">Нет записей</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-muted-foreground">
                    <th className="text-left py-2 pr-4">Время</th>
                    <th className="text-left py-2 pr-4">Пользователь</th>
                    <th className="text-left py-2 pr-4">Действие</th>
                    <th className="text-left py-2 pr-4">Сущность</th>
                    <th className="text-left py-2 pr-4">ID</th>
                    <th className="text-left py-2">IP</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.map((log) => (
                    <tr key={log.id} className="border-b hover:bg-muted/30">
                      <td className="py-2 pr-4 text-muted-foreground whitespace-nowrap">
                        {formatDateTime(log.created_at)}
                      </td>
                      <td className="py-2 pr-4">{log.user_id ?? "—"}</td>
                      <td className="py-2 pr-4">
                        <Badge variant={ACTION_VARIANTS[log.action] ?? "default"}>
                          {log.action}
                        </Badge>
                      </td>
                      <td className="py-2 pr-4">{log.entity_type}</td>
                      <td className="py-2 pr-4">{log.entity_id ?? "—"}</td>
                      <td className="py-2">{log.ip_address ?? "—"}</td>
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

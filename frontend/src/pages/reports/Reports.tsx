import { useState } from "react";
import { Download } from "lucide-react";
import api from "@/api/axios";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function Reports() {
  const today = new Date();
  const [year, setYear] = useState(today.getFullYear());
  const [month, setMonth] = useState(today.getMonth() + 1);
  const [loading, setLoading] = useState<"excel" | "pdf" | null>(null);

  const download = async (format: "excel" | "pdf") => {
    setLoading(format);
    try {
      const endpoint = format === "excel" ? "/reports/timesheet/excel" : "/reports/timesheet/pdf";
      const res = await api.get(endpoint, {
        params: { year, month },
        responseType: "blob",
      });
      const ext = format === "excel" ? "xlsx" : "pdf";
      const mime = format === "excel"
        ? "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        : "application/pdf";
      const url = URL.createObjectURL(new Blob([res.data], { type: mime }));
      const a = document.createElement("a");
      a.href = url;
      a.download = `timesheet_${year}_${String(month).padStart(2, "0")}.${ext}`;
      a.click();
      URL.revokeObjectURL(url);
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Отчёты</h1>

      <Card className="max-w-lg">
        <CardHeader>
          <CardTitle className="text-base">Отчёт по табелю</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <Label>Год</Label>
              <Input
                type="number"
                value={year}
                min={2020}
                max={2030}
                onChange={(e) => setYear(parseInt(e.target.value))}
              />
            </div>
            <div className="space-y-1">
              <Label>Месяц</Label>
              <Input
                type="number"
                value={month}
                min={1}
                max={12}
                onChange={(e) => setMonth(parseInt(e.target.value))}
              />
            </div>
          </div>
          <div className="flex gap-3">
            <Button
              className="flex-1 gap-2"
              onClick={() => download("excel")}
              disabled={loading !== null}
            >
              <Download className="h-4 w-4" />
              {loading === "excel" ? "Загрузка..." : "Excel (.xlsx)"}
            </Button>
            <Button
              variant="outline"
              className="flex-1 gap-2"
              onClick={() => download("pdf")}
              disabled={loading !== null}
            >
              <Download className="h-4 w-4" />
              {loading === "pdf" ? "Загрузка..." : "PDF"}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

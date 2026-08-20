import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

export function DashboardPage() {
  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10 text-slate-100">
      <div className="mx-auto max-w-6xl">
        <div className="mb-8">
          <p className="text-sm font-medium uppercase tracking-wider text-slate-400">
            Binance Futures AI
          </p>

          <h1 className="mt-2 text-3xl font-bold tracking-tight">
            Market Intelligence
          </h1>

          <p className="mt-2 text-sm text-slate-400">
            Sistem kontrol paneli
          </p>
        </div>

        <Card className="max-w-md border-slate-800 bg-slate-900 text-slate-100">
          <CardHeader>
            <CardTitle>Backend Status</CardTitle>

            <CardDescription className="text-slate-400">
              Backend bağlantı durumu
            </CardDescription>
          </CardHeader>

          <CardContent>
            <div className="flex items-center gap-3">
              <span className="h-3 w-3 rounded-full bg-amber-400" />

              <div>
                <p className="font-medium">Bekleniyor</p>

                <p className="text-sm text-slate-400">
                  Backend henüz kurulmadı.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </main>
  )
}
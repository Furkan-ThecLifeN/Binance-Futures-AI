import { useQuery } from "@tanstack/react-query"

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

import { getBackendHealth } from "@/services/api"


export function DashboardPage() {
  const {
    data,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ["backend-health"],
    queryFn: getBackendHealth,
    refetchInterval: 5000,
    retry: 1,
  })


  const isOnline = data?.status === "ok"


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
              FastAPI servis bağlantı durumu
            </CardDescription>
          </CardHeader>


          <CardContent>
            {isLoading && (
              <div className="flex items-center gap-3">
                <span className="h-3 w-3 animate-pulse rounded-full bg-amber-400" />

                <div>
                  <p className="font-medium">
                    Kontrol Ediliyor
                  </p>

                  <p className="text-sm text-slate-400">
                    Backend bağlantısı kontrol ediliyor.
                  </p>
                </div>
              </div>
            )}


            {isError && (
              <div className="flex items-center gap-3">
                <span className="h-3 w-3 rounded-full bg-red-500" />

                <div>
                  <p className="font-medium text-red-400">
                    Offline
                  </p>

                  <p className="text-sm text-slate-400">
                    FastAPI backend bağlantısı kurulamadı.
                  </p>
                </div>
              </div>
            )}


            {!isLoading && !isError && isOnline && data && (
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <span className="h-3 w-3 rounded-full bg-emerald-500" />

                  <div>
                    <p className="font-medium text-emerald-400">
                      Online
                    </p>

                    <p className="text-sm text-slate-400">
                      FastAPI backend çalışıyor.
                    </p>
                  </div>
                </div>


                <div className="border-t border-slate-800 pt-4">
                  <dl className="space-y-2 text-sm">
                    <div className="flex justify-between gap-4">
                      <dt className="text-slate-400">
                        Servis
                      </dt>

                      <dd className="text-right">
                        {data.service}
                      </dd>
                    </div>


                    <div className="flex justify-between gap-4">
                      <dt className="text-slate-400">
                        Sürüm
                      </dt>

                      <dd>
                        {data.version}
                      </dd>
                    </div>


                    <div className="flex justify-between gap-4">
                      <dt className="text-slate-400">
                        Ortam
                      </dt>

                      <dd>
                        {data.environment}
                      </dd>
                    </div>
                  </dl>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </main>
  )
}
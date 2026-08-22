import {
  useEffect,
  useState,
} from "react"

import { DashboardPage } from "./pages/DashboardPage"
import SymbolPage from "./pages/SymbolPage"


function App() {
  const [
    pathname,
    setPathname,
  ] = useState(
    window.location.pathname,
  )


  useEffect(() => {
    const handler = () => {
      setPathname(
        window.location.pathname,
      )
    }

    window.addEventListener(
      "popstate",
      handler,
    )

    return () => {
      window.removeEventListener(
        "popstate",
        handler,
      )
    }
  }, [])


  const navigate = (
    path: string,
  ) => {
    window.history.pushState(
      {},
      "",
      path,
    )

    setPathname(
      path,
    )
  }


  const isSymbolPage =
    pathname.startsWith(
      "/symbol/",
    )


  return (
    <div
      className="
        min-h-screen
        bg-[#000000]
        text-white
      "
    >
      <nav
        className="
          flex
          items-center
          gap-3
          border-b
          border-neutral-900
          bg-[#000000]
          px-6
          py-3
        "
      >
        <button
          onClick={() =>
            navigate("/")
          }
          className="
            rounded-lg
            px-4
            py-2
            text-sm
            text-neutral-400
            transition
            hover:bg-neutral-900
            hover:text-white
          "
        >
          Dashboard
        </button>

        <button
          onClick={() =>
            navigate(
              "/symbol/BTCUSDT",
            )
          }
          className="
            rounded-lg
            bg-neutral-950
            px-4
            py-2
            text-sm
            text-white
          "
        >
          BTCUSDT
        </button>
      </nav>

      {isSymbolPage
        ? <SymbolPage />
        : <DashboardPage />}
    </div>
  )
}


export default App
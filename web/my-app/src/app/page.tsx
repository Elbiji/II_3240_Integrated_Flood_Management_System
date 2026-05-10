import FloodLineChart from "@/components/charts/WaterHeight_Chart";
import ServerClock from "@/components/ui/ServerClock";

export default function Home() {
  return (
    <div className="min-h-screen bg-zinc-50 font-sans">
      <nav className="fixed top-0 left-0 w-full bg-blue-950 border-b border-zinc-200 z-50 px-20 py-4">
        <div className="flex flex-row p-2 justify-between gap-3">
          <div className="flex flex-row gap-6">
            {/* <div className="self-stretch w-px bg-white"></div> */}
            <h1 className="text-xl font-medium text-white w-52">Sistem Informasi <a className="font-medium">Banjir Terpadu</a></h1>
          </div>
        </div>
      </nav>

      {/* Main Content Area */}
      <main className="flex flex-col pt-14 px-20 mt-24 gap-6">

        <ServerClock />
        <FloodLineChart />
      </main>
    </div>
  );
}

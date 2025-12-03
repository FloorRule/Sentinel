import { DashboardContent } from "./DashboardContent";

function DashboardLayout() {
  return (
    <div className="flex px-[250px] h-screen w-screen bg-muted/40">

      {/* 2. MAIN CONTENT - Scrollable */}
      <main className="flex flex-1 flex-col overflow-y-auto">
        <div className="flex p-6 justify-center">
          <h2 className="text-xl font-bold tracking-tight">[Sentinel]</h2>
        </div>
        <div className="p-8 md:p-12 space-y-8">
           <DashboardContent />
        </div>
      </main>
      
    </div>
  );
}

export default DashboardLayout

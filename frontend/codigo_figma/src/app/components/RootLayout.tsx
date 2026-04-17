import { Outlet, useLocation, useNavigate } from "react-router";
import { Home, Building2 } from "lucide-react";
import { useEffect, useState } from "react";

export function RootLayout() {
  const location = useLocation();
  const navigate = useNavigate();
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);

  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 768);
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const navItems = [
    { path: "/", icon: Home, label: "Imóveis" },
  ];

  const isActive = (path: string) => {
    if (path === "/") return location.pathname === "/" || location.pathname.startsWith("/property/");
    return location.pathname.startsWith(path);
  };

  if (isMobile) {
    return (
      <div className="h-screen flex flex-col bg-background">
        <header className="bg-card border-b border-border p-4">
          <div className="flex items-center gap-2">
            <Building2 className="w-6 h-6 text-primary" />
            <h1 className="text-lg font-semibold text-primary">ImóvelHub</h1>
          </div>
        </header>
        <main className="flex-1 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    );
  }

  return (
    <div className="h-screen flex bg-background">
      <aside className="w-64 bg-card border-r border-border flex flex-col">
        <div className="p-6 border-b border-border flex items-center gap-3">
          <Building2 className="w-8 h-8 text-primary" />
          <h1 className="text-lg font-semibold text-primary">ImóvelHub</h1>
        </div>
        <nav className="flex-1 p-4 space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.path);
            return (
              <button
                key={item.path}
                onClick={() => navigate(item.path)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                  active
                    ? "bg-primary text-primary-foreground"
                    : "text-foreground hover:bg-secondary"
                }`}
              >
                <Icon className="w-5 h-5" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </aside>
      <main className="flex-1 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
}

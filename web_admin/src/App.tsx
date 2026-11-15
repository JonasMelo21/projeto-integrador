import { useEffect, useMemo, useState } from "react";
import {
  ArrowDownRight,
  ArrowUpRight,
  BarChart3,
  Bell,
  Building2,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  Edit3,
  LayoutDashboard,
  Menu,
  MoreHorizontal,
  Plus,
  RefreshCw,
  Search,
  ShieldCheck,
  SlidersHorizontal,
  Sparkles,
  Trash2,
  TrendingUp,
  X,
} from "lucide-react";
import { createClient } from "@supabase/supabase-js";

const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY,
);

type Classification = "Barato" | "Justo" | "Caro";
type Page = "telemetry" | "properties";
type TelemetryRow = Record<string, unknown>;
type TelemetryData = {
  interactions: TelemetryRow[];
  favorites: TelemetryRow[];
  properties: TelemetryRow[];
};

type TelemetryTable = "interacoes_app" | "favoritos" | "imoveis_classificados";

const navItems = [
  { id: "telemetry" as Page, label: "Telemetria do App", icon: LayoutDashboard },
  { id: "properties" as Page, label: "Gestão de Imóveis", icon: Building2 },
];

const pageTitles: Record<Page, { title: string; description: string }> = {
  telemetry: { title: "Telemetria do App", description: "Uso e engajamento dos usuários" },
  properties: {
    title: "Gestão de Imóveis",
    description: "Audite e classifique os anúncios capturados",
  },
};

async function fetchAllRows(table: TelemetryTable): Promise<TelemetryRow[]> {
  const pageSize = 1000;
  const rows: TelemetryRow[] = [];

  for (let offset = 0; ; offset += pageSize) {
    const result =
      table === "interacoes_app"
        ? await supabase
            .from("interacoes_app")
            .select("imovel_id,tipo_interacao,created_at")
            .order("created_at", { ascending: true })
            .range(offset, offset + pageSize - 1)
        : table === "favoritos"
          ? await supabase
              .from("favoritos")
              .select("imovel_id,created_at")
              .order("created_at", { ascending: true })
              .range(offset, offset + pageSize - 1)
          : await supabase
              .from("imoveis_classificados")
              .select("id_imovel,bairro,ml_label")
              .order("id_imovel", { ascending: true })
              .range(offset, offset + pageSize - 1);

    if (result.error) {
      throw result.error;
    }

    const page = (result.data ?? []).map((row) => ({ ...row }));
    rows.push(...page);
    if (page.length < pageSize) {
      return rows;
    }
  }
}

function Brand() {
  return (
    <div className="flex items-center gap-3">
      <div className="grid size-9 place-items-center rounded-[10px] bg-blue-600 text-white shadow-lg shadow-blue-950/30">
        <Building2 size={19} strokeWidth={2.3} />
      </div>
      <div>
        <p className="text-[15px] font-semibold tracking-[-0.02em] text-white">RentMaster</p>
        <p className="mt-0.5 text-[9px] font-semibold uppercase tracking-[0.18em] text-slate-600">
          Rental Intelligence
        </p>
      </div>
    </div>
  );
}

function Sidebar({
  page,
  setPage,
  mobileOpen,
  setMobileOpen,
}: {
  page: Page;
  setPage: (page: Page) => void;
  mobileOpen: boolean;
  setMobileOpen: (open: boolean) => void;
}) {
  return (
    <>
      {mobileOpen && (
        <button
          aria-label="Fechar menu"
          className="fixed inset-0 z-40 bg-slate-950/80 backdrop-blur-sm lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}
      <aside
        className={`fixed inset-y-0 left-0 z-50 flex w-[252px] flex-col border-r border-slate-800 bg-slate-900 px-4 py-5 transition-transform duration-300 lg:translate-x-0 ${
          mobileOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex items-center justify-between px-2">
          <Brand />
          <button
            aria-label="Fechar menu"
            className="rounded-lg p-2 text-slate-500 hover:bg-slate-800/70 hover:text-white lg:hidden"
            onClick={() => setMobileOpen(false)}
          >
            <X size={18} />
          </button>
        </div>
        <div className="mt-10 px-3 text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-600">
          Workspace
        </div>
        <nav className="mt-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = page === item.id;
            return (
              <button
                key={item.id}
                onClick={() => {
                  setPage(item.id);
                  setMobileOpen(false);
                }}
                className={`group flex w-full items-center gap-3 rounded-[10px] px-3 py-2.5 text-left text-[13px] font-medium transition ${
                  active
                    ? "bg-blue-600/15 text-blue-300"
                    : "text-slate-500 hover:bg-slate-800/60 hover:text-blue-300"
                }`}
              >
                <Icon size={17} strokeWidth={active ? 2.1 : 1.8} />
                <span className="flex-1">{item.label}</span>
                {active && <span className="size-1.5 rounded-full bg-blue-500" />}
              </button>
            );
          })}
        </nav>

        <div className="mt-auto">
          <div className="mb-4 rounded-xl border border-slate-800 bg-slate-800/60 p-3">
            <div className="flex items-center gap-2 text-[11px] text-slate-500">
              <ShieldCheck size={14} />
              <span>Sistema operacional</span>
            </div>
            <div className="mt-2 h-1 overflow-hidden rounded-full bg-slate-800">
              <div className="h-full w-[92%] rounded-full bg-blue-500" />
            </div>
            <p className="mt-2 text-[10px] text-slate-600">Última sincronização há 12 min</p>
          </div>
          <button className="flex w-full items-center gap-3 rounded-xl border-t border-slate-800 px-2 pt-4 text-left">
            <div className="grid size-9 place-items-center rounded-full bg-slate-800 text-xs font-semibold text-slate-200">
              AM
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-xs font-semibold text-slate-200">André Martins</p>
              <p className="mt-0.5 text-[10px] text-slate-600">Administrador</p>
            </div>
            <MoreHorizontal size={16} className="text-slate-600" />
          </button>
        </div>
      </aside>
    </>
  );
}

function Header({
  page,
  setMobileOpen,
  onSync,
  syncing,
}: {
  page: Page;
  setMobileOpen: (open: boolean) => void;
  onSync: () => void;
  syncing: boolean;
}) {
  const content = pageTitles[page];
  return (
    <header className="flex min-h-[82px] items-center justify-between gap-4 border-b border-slate-800 px-5 md:px-8">
      <div className="flex items-center gap-3">
        <button
          aria-label="Abrir menu"
          className="rounded-lg border border-slate-800 p-2 text-slate-400 lg:hidden"
          onClick={() => setMobileOpen(true)}
        >
          <Menu size={18} />
        </button>
        <div>
          <h1 className="text-lg font-semibold tracking-[-0.025em] text-slate-100 md:text-xl">
            {content.title}
          </h1>
          <p className="mt-1 hidden text-[11px] text-slate-600 sm:block">{content.description}</p>
        </div>
      </div>
      <div className="flex items-center gap-2">
        <button
          aria-label="Notificações"
          className="relative rounded-[10px] border border-slate-800 p-2.5 text-slate-500 hover:text-slate-200"
        >
          <Bell size={16} />
          <span className="absolute right-2 top-2 size-1.5 rounded-full bg-blue-500 ring-2 ring-slate-950" />
        </button>
        {page === "properties" && (
          <button
            onClick={onSync}
            disabled={syncing}
            className="flex items-center gap-2 rounded-[10px] bg-blue-600 px-3.5 py-2.5 text-xs font-semibold text-white shadow-lg shadow-blue-950/25 transition hover:bg-blue-700 disabled:opacity-70 md:px-4"
          >
            <RefreshCw size={15} className={syncing ? "animate-spin" : ""} />
            <span className="hidden sm:inline">
              {syncing ? "Sincronizando..." : "Sincronizar Scraper"}
            </span>
            <span className="sm:hidden">Sincronizar</span>
          </button>
        )}
      </div>
    </header>
  );
}

function MetricCard({
  label,
  value,
  change,
  icon: Icon,
  direction,
}: {
  label: string;
  value: string;
  change: string;
  icon: typeof Building2;
  direction: "up" | "down";
}) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-[11px] font-medium text-slate-500">{label}</p>
          <p className="mt-3 text-[26px] font-semibold tracking-[-0.045em] text-slate-100">
            {value}
          </p>
        </div>
        <div className="grid size-9 place-items-center rounded-xl border border-blue-500/15 bg-blue-600/10 text-blue-400">
          <Icon size={17} />
        </div>
      </div>
      <div className="mt-4 flex items-center gap-1.5 text-[10px]">
        {direction === "up" ? <ArrowUpRight size={13} /> : <ArrowDownRight size={13} />}
        <span className="font-semibold text-blue-400">{change}</span>
      </div>
    </div>
  );
}

function ClassificationBadge({ value }: { value: Classification }) {
  const style = {
    Barato: "border-emerald-400/15 bg-emerald-400/10 text-emerald-400",
    Justo: "border-amber-400/15 bg-amber-400/10 text-amber-300",
    Caro: "border-red-400/15 bg-red-400/10 text-red-400",
  }[value];
  return (
    <span
      className={`inline-flex min-w-[66px] items-center justify-center rounded-full border px-2.5 py-1 text-[10px] font-semibold ${style}`}
    >
      {value}
    </span>
  );
}

function normalizeClassification(value: unknown): Classification | null {
  const normalized = String(value ?? "")
    .trim()
    .replace(/^preço\s+/i, "")
    .toLocaleLowerCase("pt-BR");
  if (normalized === "barato") return "Barato";
  if (normalized === "justo") return "Justo";
  if (normalized === "caro") return "Caro";
  return null;
}

function PropertiesPage({ onOpenModal }: { onOpenModal: () => void }) {
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<"Todos" | Classification>("Todos");
  const [bairroFilter, setBairroFilter] = useState("Todos");
  const [imoveis, setImoveis] = useState<any[]>([]);

  useEffect(() => {
    const loadImoveis = async () => {
      try {
        const { data, error } = await supabase.from("imoveis_classificados").select("*");

        if (error) {
          throw error;
        }

        setImoveis(data ?? []);
      } catch (error) {
        console.error("Erro ao carregar imóveis:", error);
      }
    };

    void loadImoveis();
  }, []);

  const handleDelete = async (imovel: any) => {
    const originalIndex = imoveis.findIndex((item) => item.id_imovel === imovel.id_imovel);
    setImoveis((items) => items.filter((item) => item.id_imovel !== imovel.id_imovel));

    try {
      const { error } = await supabase
        .from("imoveis_classificados")
        .delete()
        .eq("id_imovel", imovel.id_imovel);

      if (error) {
        throw error;
      }
    } catch (error) {
      console.error("Erro ao excluir imóvel:", error);
      setImoveis((items) => {
        if (items.some((item) => item.id_imovel === imovel.id_imovel)) {
          return items;
        }

        const restoredItems = [...items];
        restoredItems.splice(Math.min(originalIndex, restoredItems.length), 0, imovel);
        return restoredItems;
      });
      window.alert("Não foi possível excluir o imóvel. Tente novamente.");
    }
  };

  const filtered = useMemo(
    () =>
      imoveis.filter((imovel) => {
        const classification = normalizeClassification(imovel.ml_label);
        return (
          (filter === "Todos" || classification === filter) &&
          (bairroFilter === "Todos" || imovel.bairro === bairroFilter) &&
          `${imovel.id_imovel ?? ""} ${imovel.bairro ?? ""}`
            .toLowerCase()
            .includes(query.toLowerCase())
        );
      }),
    [query, filter, bairroFilter, imoveis],
  );
  const bairros = useMemo(
    () =>
      [...new Set(imoveis.map((imovel) => imovel.bairro).filter(Boolean))].sort((a, b) =>
        String(a).localeCompare(String(b), "pt-BR"),
      ),
    [imoveis],
  );
  const totalCaros = filtered.filter(
    (imovel) => normalizeClassification(imovel.ml_label) === "Caro",
  ).length;
  const totalBaratos = filtered.filter(
    (imovel) => normalizeClassification(imovel.ml_label) === "Barato",
  ).length;

  return (
    <div className="space-y-6">
      <section className="grid gap-3 sm:grid-cols-3">
        <MetricCard
          label="Total de imóveis"
          value={filtered.length.toLocaleString("pt-BR")}
          change={
            filter !== "Todos"
              ? `Filtro: ${filter}`
              : bairroFilter !== "Todos"
                ? bairroFilter
                : "Todos os bairros"
          }
          icon={Building2}
          direction="up"
        />
        <MetricCard
          label="Anomalias / Supervalorizados"
          value={totalCaros.toLocaleString("pt-BR")}
          change="Classificados como caros"
          icon={TrendingUp}
          direction="up"
        />
        <MetricCard
          label="Oportunidades / Baratos"
          value={totalBaratos.toLocaleString("pt-BR")}
          change="Classificados como baratos"
          icon={Sparkles}
          direction="down"
        />
      </section>

      <section className="overflow-hidden rounded-2xl border border-slate-800 bg-slate-900">
        <div className="flex flex-col justify-between gap-4 border-b border-slate-800 p-4 sm:flex-row sm:items-center">
          <div className="flex flex-1 flex-col gap-2 sm:flex-row">
            <label className="relative block w-full sm:max-w-[310px]">
              <Search
                className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-600"
                size={15}
              />
              <input
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Buscar por ID ou bairro"
                className="h-10 w-full rounded-[10px] border border-slate-800 bg-slate-950 pl-9 pr-3 text-xs text-slate-200 outline-none transition placeholder:text-slate-700 focus:border-blue-500"
              />
            </label>
            <label className="relative block sm:w-[174px]">
              <SlidersHorizontal
                className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-600"
                size={14}
              />
              <select
                value={filter}
                onChange={(event) => setFilter(event.target.value as "Todos" | Classification)}
                className="h-10 w-full appearance-none rounded-[10px] border border-slate-800 bg-slate-950 pl-9 pr-8 text-xs text-slate-400 outline-none focus:border-blue-500"
              >
                <option>Todos</option>
                <option>Barato</option>
                <option>Justo</option>
                <option>Caro</option>
              </select>
              <ChevronDown
                className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-slate-600"
                size={14}
              />
            </label>
            <label className="relative block sm:w-[190px]">
              <select
                value={bairroFilter}
                onChange={(event) => setBairroFilter(event.target.value)}
                aria-label="Filtrar por bairro"
                className="h-10 w-full appearance-none rounded-[10px] border border-slate-800 bg-slate-950 px-3 pr-8 text-xs text-slate-400 outline-none focus:border-blue-500"
              >
                <option value="Todos">Todos os bairros</option>
                {bairros.map((bairro) => (
                  <option key={bairro} value={bairro}>
                    {bairro}
                  </option>
                ))}
              </select>
              <ChevronDown
                className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-slate-600"
                size={14}
              />
            </label>
          </div>
          <button
            onClick={onOpenModal}
            className="flex h-10 items-center justify-center gap-2 rounded-[10px] bg-blue-600 px-3.5 text-xs font-semibold text-white transition hover:bg-blue-700"
          >
            <Plus size={15} />
            Adicionar imóvel
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full min-w-[790px] text-left">
            <thead>
              <tr className="border-b border-slate-800 text-[9px] font-semibold uppercase tracking-[0.13em] text-slate-600">
                <th className="w-[92px] px-5 py-3.5">Imóvel</th>
                <th className="px-3 py-3.5">Bairro</th>
                <th className="px-3 py-3.5">Valor</th>
                <th className="px-3 py-3.5">Área</th>
                <th className="px-3 py-3.5">Classificação</th>
                <th className="px-3 py-3.5">Confiança</th>
                <th className="px-5 py-3.5 text-right">Ações</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((imovel, index) => {
                const classification = normalizeClassification(imovel.ml_label);
                return (
                  <tr
                    key={imovel.id_imovel ?? `${imovel.bairro ?? "imovel"}-${index}`}
                    className="group border-b border-slate-800 transition last:border-0 hover:bg-slate-800/60"
                  >
                    <td className="px-5 py-3">
                      <img
                        src={imovel.imagem ?? ""}
                        alt={`Imóvel em ${imovel.bairro ?? ""}`}
                        className="size-10 rounded-[9px] object-cover"
                      />
                    </td>
                    <td className="px-3 py-3">
                      <p className="text-xs font-semibold text-slate-200">{imovel.bairro}</p>
                      <p className="mt-1 text-[10px] text-slate-600">{imovel.id_imovel ?? "—"}</p>
                    </td>
                    <td className="px-3 py-3 text-xs font-medium tabular-nums text-slate-300">
                      {imovel.preco == null
                        ? "—"
                        : Number(imovel.preco).toLocaleString("pt-BR", {
                            style: "currency",
                            currency: "BRL",
                            minimumFractionDigits: 0,
                          })}
                    </td>
                    <td className="px-3 py-3 text-xs tabular-nums text-slate-400">
                      {imovel.area == null ? "—" : `${imovel.area} m²`}
                    </td>
                    <td className="px-3 py-3">
                      {classification && <ClassificationBadge value={classification} />}
                    </td>
                    <td className="px-3 py-3">
                      <div className="flex items-center gap-2">
                        <div className="h-1 w-12 overflow-hidden rounded-full bg-slate-800">
                          <div
                            className="h-full rounded-full bg-blue-500"
                            style={{ width: "0%" }}
                          />
                        </div>
                        <span className="text-[10px] tabular-nums text-slate-600">—</span>
                      </div>
                    </td>
                    <td className="px-5 py-3">
                      <div className="flex items-center justify-end gap-1">
                        <button
                          aria-label={`Editar ${imovel.id_imovel ?? "imóvel"}`}
                          className="rounded-lg p-2 text-slate-600 transition hover:bg-slate-800/70 hover:text-slate-200"
                        >
                          <Edit3 size={14} />
                        </button>
                        <button
                          aria-label={`Excluir ${imovel.id_imovel ?? "imóvel"}`}
                          onClick={() => void handleDelete(imovel)}
                          className="rounded-lg p-2 text-slate-600 transition hover:bg-slate-800/70 hover:text-red-400"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          {filtered.length === 0 && (
            <div className="px-5 py-14 text-center">
              <Search size={20} className="mx-auto text-slate-700" />
              <p className="mt-3 text-xs font-medium text-slate-400">Nenhum imóvel encontrado</p>
              <p className="mt-1 text-[10px] text-slate-600">
                Tente ajustar sua busca ou classificação.
              </p>
            </div>
          )}
        </div>
        <div className="flex items-center justify-between border-t border-slate-800 px-5 py-3.5">
          <p className="text-[10px] text-slate-600">
            Exibindo <span className="text-slate-400">{filtered.length}</span> de {imoveis.length}{" "}
            registros
          </p>
          <div className="flex items-center gap-1">
            <button
              aria-label="Página anterior"
              className="rounded-lg border border-slate-800 p-1.5 text-slate-700"
            >
              <ChevronLeft size={14} />
            </button>
            <button className="grid size-7 place-items-center rounded-lg bg-blue-600 text-[10px] text-white">
              1
            </button>
            <button className="grid size-7 place-items-center rounded-lg text-[10px] text-slate-600 hover:bg-slate-800/60">
              2
            </button>
            <button className="grid size-7 place-items-center rounded-lg text-[10px] text-slate-600 hover:bg-slate-800/60">
              3
            </button>
            <button
              aria-label="Próxima página"
              className="rounded-lg border border-slate-800 p-1.5 text-slate-400"
            >
              <ChevronRight size={14} />
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}

function getRecordDate(row: TelemetryRow): Date | null {
  const rawDate = row.created_at ?? row.timestamp ?? row.data_criacao;
  if (typeof rawDate !== "string" && typeof rawDate !== "number") {
    return null;
  }

  const date = new Date(rawDate);
  return Number.isNaN(date.getTime()) ? null : date;
}

function TelemetryDashboard({
  data,
  loading,
  error,
}: {
  data: TelemetryData;
  loading: boolean;
  error: string | null;
}) {
  const propertyById = new Map(
    data.properties.map((property) => [String(property.id_imovel ?? ""), property]),
  );
  const interactionEvents = data.interactions.flatMap((interaction) => {
    const type = interaction.tipo_interacao;
    if (type !== "clique" && type !== "compartilhamento" && type !== "favorito") {
      return [];
    }

    return [
      {
        action: type,
        propertyId: String(interaction.imovel_id ?? ""),
        date: getRecordDate(interaction),
      },
    ];
  });
  const events = interactionEvents;
  const clickCount = interactionEvents.filter((event) => event.action === "clique").length;
  const shareCount = interactionEvents.filter(
    (event) => event.action === "compartilhamento",
  ).length;
  const neighborhoodCounts = new Map<string, number>();

  for (const event of events) {
    const property = propertyById.get(event.propertyId);
    const neighborhood =
      typeof property?.bairro === "string" && property.bairro.trim()
        ? property.bairro
        : "Bairro não informado";
    neighborhoodCounts.set(neighborhood, (neighborhoodCounts.get(neighborhood) ?? 0) + 1);
  }

  const topNeighborhoods = [...neighborhoodCounts.entries()]
    .map(([neighborhood, count]) => ({ neighborhood, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 5);
  const maxNeighborhoodCount = Math.max(...topNeighborhoods.map(({ count }) => count), 1);
  const recentEvents = [...events]
    .sort((a, b) => (b.date?.getTime() ?? 0) - (a.date?.getTime() ?? 0))
    .slice(0, 5);

  return (
    <div className="space-y-6">
      <section className="grid gap-3 sm:grid-cols-3">
        <MetricCard
          label="Total de Cliques"
          value={loading ? "—" : clickCount.toLocaleString("pt-BR")}
          change="Eventos registrados"
          icon={TrendingUp}
          direction="up"
        />
        <MetricCard
          label="Compartilhamentos"
          value={loading ? "—" : shareCount.toLocaleString("pt-BR")}
          change="Eventos registrados"
          icon={BarChart3}
          direction="up"
        />
        <MetricCard
          label="Imóveis Favoritados"
          value={loading ? "—" : data.favorites.length.toLocaleString("pt-BR")}
          change="Favoritos atuais"
          icon={Building2}
          direction="up"
        />
      </section>

      {error && (
        <p
          role="alert"
          className="rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-xs text-red-300"
        >
          {error}
        </p>
      )}

      <section className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
        <div>
          <h2 className="text-sm font-semibold text-slate-200">Ranking de Bairros</h2>
          <p className="mt-1 text-[10px] text-slate-600">Bairros com mais interações no app</p>
        </div>
        {topNeighborhoods.length > 0 ? (
          <div className="mt-6 space-y-4">
            {topNeighborhoods.map(({ neighborhood, count }) => (
              <div key={neighborhood} className="flex items-center gap-4">
                <span className="w-36 shrink-0 truncate text-xs text-slate-400">
                  {neighborhood}
                </span>
                <div className="h-2 flex-1 overflow-hidden rounded-full bg-slate-800">
                  <div
                    className="h-full rounded-full bg-blue-600"
                    style={{ width: `${(count / maxNeighborhoodCount) * 100}%` }}
                  />
                </div>
                <span className="w-8 text-right text-xs tabular-nums text-slate-300">{count}</span>
              </div>
            ))}
          </div>
        ) : (
          <p className="mt-6 text-xs text-slate-500">
            {loading ? "Carregando interações..." : "Ainda não há interações registradas."}
          </p>
        )}
      </section>

      <section className="overflow-hidden rounded-2xl border border-slate-800 bg-slate-900">
        <div className="border-b border-slate-800 p-4">
          <h2 className="text-sm font-semibold text-slate-200">Interações Recentes</h2>
          <p className="mt-1 text-[10px] text-slate-600">Últimas atividades registradas no app</p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[680px] text-left">
            <thead>
              <tr className="border-b border-slate-800 text-[9px] font-semibold uppercase tracking-[0.13em] text-slate-600">
                <th className="px-5 py-3.5">Ação</th>
                <th className="px-3 py-3.5">Bairro do Imóvel</th>
                <th className="px-3 py-3.5">Classificação</th>
                <th className="px-5 py-3.5">Data/Hora</th>
              </tr>
            </thead>
            <tbody>
              {recentEvents.map((event, index) => {
                const property = propertyById.get(event.propertyId);
                const classification = normalizeClassification(property?.ml_label);
                const action =
                  event.action === "clique"
                    ? "Clique"
                    : event.action === "compartilhamento"
                      ? "Compartilhamento"
                      : "Favorito";

                return (
                  <tr
                    key={`${event.action}-${event.propertyId}-${event.date?.getTime() ?? index}`}
                    className="border-b border-slate-800 last:border-0 hover:bg-slate-800/60"
                  >
                    <td className="px-5 py-3.5 text-xs font-medium text-slate-200">{action}</td>
                    <td className="px-3 py-3.5 text-xs text-slate-400">
                      {typeof property?.bairro === "string" ? property.bairro : "—"}
                    </td>
                    <td className="px-3 py-3.5">
                      {classification ? <ClassificationBadge value={classification} /> : "—"}
                    </td>
                    <td className="px-5 py-3.5 text-xs tabular-nums text-slate-500">
                      {event.date
                        ? new Intl.DateTimeFormat("pt-BR", {
                            dateStyle: "short",
                            timeStyle: "short",
                          }).format(event.date)
                        : "—"}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          {recentEvents.length === 0 && (
            <p className="px-5 py-10 text-center text-xs text-slate-500">
              {loading ? "Carregando interações..." : "Ainda não há interações registradas."}
            </p>
          )}
        </div>
      </section>
    </div>
  );
}

function AddPropertyModal({ onClose }: { onClose: () => void }) {
  return (
    <div
      className="fixed inset-0 z-[70] grid place-items-center bg-slate-950/85 p-4 backdrop-blur-sm"
      onMouseDown={onClose}
    >
      <div
        className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900 shadow-2xl"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <div className="flex items-center justify-between border-b border-slate-800 p-5">
          <div>
            <h2 className="text-sm font-semibold text-slate-100">Adicionar imóvel</h2>
            <p className="mt-1 text-[10px] text-slate-600">
              Inclua um anúncio para auditoria manual
            </p>
          </div>
          <button
            aria-label="Fechar"
            onClick={onClose}
            className="rounded-lg p-2 text-slate-600 hover:bg-slate-800/70 hover:text-white"
          >
            <X size={16} />
          </button>
        </div>
        <div className="grid gap-4 p-5">
          {[
            ["ID do anúncio", "Ex: RM-34220"],
            ["Bairro", "Ex: Vila Mariana"],
            ["Valor mensal", "R$ 0,00"],
            ["Área", "0 m²"],
          ].map(([label, placeholder]) => (
            <label key={label} className="grid gap-2 text-[10px] font-medium text-slate-500">
              {label}
              <input
                placeholder={placeholder}
                className="h-10 rounded-[9px] border border-slate-800 bg-slate-950 px-3 text-xs text-slate-200 outline-none placeholder:text-slate-700 focus:border-blue-500"
              />
            </label>
          ))}
        </div>
        <div className="flex justify-end gap-2 border-t border-slate-800 p-4">
          <button
            onClick={onClose}
            className="rounded-[9px] px-4 py-2 text-xs font-medium text-slate-500 hover:text-white"
          >
            Cancelar
          </button>
          <button
            onClick={onClose}
            className="rounded-[9px] bg-blue-600 px-4 py-2 text-xs font-semibold text-white transition hover:bg-blue-700"
          >
            Adicionar imóvel
          </button>
        </div>
      </div>
    </div>
  );
}

export default function App() {
  const [page, setPage] = useState<Page>("telemetry");
  const [mobileOpen, setMobileOpen] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [telemetryData, setTelemetryData] = useState<TelemetryData>({
    interactions: [],
    favorites: [],
    properties: [],
  });
  const [telemetryLoading, setTelemetryLoading] = useState(true);
  const [telemetryError, setTelemetryError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    async function loadTelemetry() {
      try {
        const [interactions, favorites, properties] = await Promise.all([
          fetchAllRows("interacoes_app"),
          fetchAllRows("favoritos"),
          fetchAllRows("imoveis_classificados"),
        ]);

        if (isMounted) {
          setTelemetryData({ interactions, favorites, properties });
          setTelemetryError(null);
        }
      } catch (error) {
        console.error("Erro ao carregar telemetria do app:", error);
        if (isMounted) {
          setTelemetryError(
            "Não foi possível carregar a telemetria. Verifique a conexão e as políticas RLS do Supabase.",
          );
        }
      } finally {
        if (isMounted) {
          setTelemetryLoading(false);
        }
      }
    }

    void loadTelemetry();
    return () => {
      isMounted = false;
    };
  }, []);

  const handleSync = () => {
    if (syncing) return;
    setSyncing(true);
    window.setTimeout(() => setSyncing(false), 1400);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <Sidebar
        page={page}
        setPage={setPage}
        mobileOpen={mobileOpen}
        setMobileOpen={setMobileOpen}
      />
      <div className="min-h-screen lg:pl-[252px]">
        <Header page={page} setMobileOpen={setMobileOpen} onSync={handleSync} syncing={syncing} />
        <main className="mx-auto max-w-[1420px] p-5 md:p-8">
          {page === "properties" && <PropertiesPage onOpenModal={() => setModalOpen(true)} />}
          {page === "telemetry" && (
            <TelemetryDashboard
              data={telemetryData}
              loading={telemetryLoading}
              error={telemetryError}
            />
          )}
        </main>
      </div>
      {modalOpen && <AddPropertyModal onClose={() => setModalOpen(false)} />}
    </div>
  );
}

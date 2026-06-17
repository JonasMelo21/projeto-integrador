import { useState } from "react";
import { Search, SlidersHorizontal } from "lucide-react";
import { PropertyCard } from "./PropertyCard";
import { mockProperties } from "../data/mockData";

export function HomePage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedFilter, setSelectedFilter] = useState("Todos");
  const [areaMin, setAreaMin] = useState(0);
  const [areaMax, setAreaMax] = useState(200);
  const [priceMax, setPriceMax] = useState(10000);

  const filters = [
    "Todos",
    "Apartamento",
    "Casa",
    "Studio",
    "Preço Justo",
    "Oportunidade",
  ];

  const filteredProperties = mockProperties.filter((property) => {
    // Filtro de categoria
    if (selectedFilter !== "Todos") {
      if (selectedFilter === "Apartamento" && !property.title.toLowerCase().includes("apartamento")) return false;
      if (selectedFilter === "Casa" && !property.title.toLowerCase().includes("casa")) return false;
      if (selectedFilter === "Studio" && !property.title.toLowerCase().includes("studio") && !property.title.toLowerCase().includes("kitnet") && !property.title.toLowerCase().includes("loft")) return false;
      if (selectedFilter === "Preço Justo" && property.mlTag !== "Preço Justo") return false;
      if (selectedFilter === "Oportunidade" && property.mlTag !== "Oportunidade") return false;
    }

    // Filtro de área
    if (property.area < areaMin || property.area > areaMax) return false;

    // Filtro de preço
    if (property.price > priceMax) return false;

    return true;
  });

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-7xl mx-auto px-4 py-6 md:py-8">
        <div className="mb-6 md:mb-8">
          <div className="flex items-center gap-3 mb-6">
            <div className="flex-1 relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Buscar por localização, bairro ou cidade..."
                className="w-full pl-12 pr-4 py-3 md:py-4 border border-border rounded-xl bg-card focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all shadow-sm"
              />
            </div>
            <button className="p-3 md:p-4 border border-border rounded-xl bg-card hover:bg-secondary transition-colors shadow-sm">
              <SlidersHorizontal className="w-5 h-5 text-foreground" />
            </button>
          </div>

          <div className="flex flex-wrap gap-3 items-center">
            <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
              {filters.map((filter) => (
                <button
                  key={filter}
                  onClick={() => setSelectedFilter(filter)}
                  className={`px-4 py-2 rounded-full whitespace-nowrap transition-all ${
                    selectedFilter === filter
                      ? "bg-primary text-primary-foreground shadow-md"
                      : "bg-secondary text-secondary-foreground hover:bg-secondary/80"
                  }`}
                >
                  {filter}
                </button>
              ))}
            </div>

            <div className="flex gap-4 items-center flex-wrap">
              <div className="bg-card border border-border rounded-xl px-4 py-3 shadow-sm min-w-[240px]">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm text-muted-foreground">Área (m²)</span>
                  <span className="text-sm font-medium">{areaMin}m² - {areaMax}m²</span>
                </div>
                <div className="flex gap-3 items-center">
                  <input
                    type="range"
                    min="0"
                    max="200"
                    value={areaMin}
                    onChange={(e) => setAreaMin(Number(e.target.value))}
                    className="flex-1 accent-primary"
                  />
                  <input
                    type="range"
                    min="0"
                    max="200"
                    value={areaMax}
                    onChange={(e) => setAreaMax(Number(e.target.value))}
                    className="flex-1 accent-primary"
                  />
                </div>
              </div>

              <div className="bg-card border border-border rounded-xl px-4 py-3 shadow-sm min-w-[220px]">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm text-muted-foreground">Preço até</span>
                  <span className="text-sm font-medium">R$ {priceMax.toLocaleString('pt-BR')}</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="10000"
                  step="100"
                  value={priceMax}
                  onChange={(e) => setPriceMax(Number(e.target.value))}
                  className="w-full accent-primary"
                />
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 md:gap-6">
          {filteredProperties.map((property) => (
            <PropertyCard key={property.id} property={property} />
          ))}
        </div>
      </div>
    </div>
  );
}

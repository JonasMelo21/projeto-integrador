import { useParams, useNavigate } from "react-router";
import { useState, useEffect } from "react";
import {
  ChevronLeft,
  Heart,
  Share2,
  Bed,
  Bath,
  Maximize,
  MapPin,
  MessageCircle,
  Loader2,
  Car,
} from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Cell } from "recharts";

const API_URL = "http://localhost:8000/api";

interface BackendImovelDetail {
  id_imovel: number;
  titulo: string;
  url: string;
  preco: number;
  area_m2: number;
  quartos: number | null;
  banheiros: number | null;
  vagas: number | null;
  imagem: string;
  descricao: string | null;
  imobiliaria: { nome_empresa: string } | null;
  local: { bairro: string; cidade: string; uf: string } | null;
  classificacao_preco?: string;
}

const FALLBACK_IMAGE =
  "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=800&h=600&fit=crop";

export function PropertyDetailsPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [property, setProperty] = useState<BackendImovelDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isFavorite, setIsFavorite] = useState(false);

  useEffect(() => {
    if (!id) return;
    fetch(`${API_URL}/imoveis/${id}`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json() as Promise<BackendImovelDetail>;
      })
      .then((data) => {
        setProperty(data);
        setLoading(false);
      })
      .catch(() => {
        setError("Imóvel não encontrado ou backend indisponível.");
        setLoading(false);
      });
  }, [id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen gap-3 text-muted-foreground">
        <Loader2 className="w-6 h-6 animate-spin" />
        <span>Carregando imóvel...</span>
      </div>
    );
  }

  if (error || !property) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen gap-3">
        <p className="text-destructive">{error ?? "Imóvel não encontrado"}</p>
        <button onClick={() => navigate("/")} className="text-primary underline text-sm">
          Voltar para a lista
        </button>
      </div>
    );
  }

  const image = property.imagem || FALLBACK_IMAGE;
  const location = property.local
    ? `${property.local.bairro}, ${property.local.cidade} - ${property.local.uf}`
    : "Brasília - DF";

  const priceData = [
    { name: "Mínimo", value: Math.round(property.preco * 0.8) },
    { name: "Médio", value: Math.round(property.preco * 1.0) },
    { name: "Este Imóvel", value: property.preco },
    { name: "Máximo", value: Math.round(property.preco * 1.3) },
  ];

  return (
    <div className="min-h-screen bg-background">
      <div className="sticky top-0 z-10 bg-card border-b border-border px-4 py-3 flex items-center justify-between">
        <button
          onClick={() => navigate("/")}
          className="p-2 hover:bg-secondary rounded-full transition-colors"
        >
          <ChevronLeft className="w-6 h-6" />
        </button>
        <div className="flex gap-2">
          <button
            onClick={() => setIsFavorite(!isFavorite)}
            className="p-2 hover:bg-secondary rounded-full transition-colors"
          >
            <Heart className={`w-6 h-6 ${isFavorite ? "fill-red-500 text-red-500" : ""}`} />
          </button>
          <a
            href={property.url}
            target="_blank"
            rel="noopener noreferrer"
            className="p-2 hover:bg-secondary rounded-full transition-colors"
          >
            <Share2 className="w-6 h-6" />
          </a>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 py-6 md:py-8">
        <div className="relative mb-6 rounded-2xl overflow-hidden">
          <div className="aspect-video md:aspect-[21/9] bg-muted">
            <img src={image} alt={property.titulo} className="w-full h-full object-cover" />
          </div>
        </div>

        <div className="grid md:grid-cols-3 gap-6 md:gap-8">
          <div className="md:col-span-2 space-y-6">
            <div>
              <div className="flex flex-col items-start gap-3 mb-2">
                <span className={`px-3 py-1 rounded-full text-xs font-semibold shadow-sm ${
                  property.classificacao_preco === "Barato" ? "bg-green-100 text-green-800" :
                  property.classificacao_preco === "Preço Justo" ? "bg-blue-100 text-blue-800" :
                  property.classificacao_preco === "Caro" ? "bg-red-100 text-red-800" :
                  "bg-gray-100 text-gray-800"
                }`}>
                  Análise ML: {property.classificacao_preco || "Não Avaliado"}
                </span>
                <h1 className="text-2xl md:text-3xl font-bold">{property.titulo}</h1>
              </div>
              <div className="flex items-center gap-2 text-muted-foreground mb-4">
                <MapPin className="w-5 h-5" />
                <span>{location}</span>
              </div>

              <div className="flex items-center gap-6 py-4 border-y border-border flex-wrap">
                {property.quartos != null && (
                  <div className="flex items-center gap-2">
                    <Bed className="w-5 h-5 text-muted-foreground" />
                    <span>{property.quartos} quartos</span>
                  </div>
                )}
                {property.banheiros != null && (
                  <div className="flex items-center gap-2">
                    <Bath className="w-5 h-5 text-muted-foreground" />
                    <span>{property.banheiros} banheiros</span>
                  </div>
                )}
                {property.vagas != null && (
                  <div className="flex items-center gap-2">
                    <Car className="w-5 h-5 text-muted-foreground" />
                    <span>{property.vagas} vagas</span>
                  </div>
                )}
                {property.area_m2 > 0 && (
                  <div className="flex items-center gap-2">
                    <Maximize className="w-5 h-5 text-muted-foreground" />
                    <span>{property.area_m2}m²</span>
                  </div>
                )}
              </div>
            </div>

            {property.descricao && (
              <div>
                <h3 className="mb-3">Descrição</h3>
                <p className="text-muted-foreground leading-relaxed whitespace-pre-wrap">
                  {property.descricao}
                </p>
              </div>
            )}

            {property.imobiliaria && (
              <div>
                <h3 className="mb-2">Imobiliária</h3>
                <span className="px-4 py-2 bg-secondary rounded-full text-sm">
                  {property.imobiliaria.nome_empresa}
                </span>
              </div>
            )}

            <div className="bg-card border border-border rounded-xl p-6">
              <h3 className="mb-4">Análise de Preço</h3>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={priceData}>
                  <XAxis
                    dataKey="name"
                    tick={{ fontSize: 12 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis hide />
                  <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                    {priceData.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={entry.name === "Este Imóvel" ? "#0A2540" : "#E8F0FE"}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="md:col-span-1">
            <div className="sticky top-20 bg-card border border-border rounded-xl p-6 shadow-lg">
              <div className="mb-6">
                <p className="text-sm text-muted-foreground mb-1">Valor do Aluguel</p>
                <p className="text-3xl text-primary mb-1">
                  R$ {property.preco.toLocaleString("pt-BR")}
                </p>
                <p className="text-sm text-muted-foreground">/mês</p>
              </div>

              <a
                href={property.url}
                target="_blank"
                rel="noopener noreferrer"
                className="w-full bg-primary text-primary-foreground py-3 rounded-lg hover:bg-primary/90 transition-all shadow-md hover:shadow-lg flex items-center justify-center gap-2 mb-3"
              >
                <MessageCircle className="w-5 h-5" />
                <span>Ver no Site</span>
              </a>

              <button className="w-full border border-border py-3 rounded-lg hover:bg-secondary transition-colors">
                Agendar Visita
              </button>

              <div className="mt-6 pt-6 border-t border-border space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Aluguel</span>
                  <span>R$ {property.preco.toLocaleString("pt-BR")}</span>
                </div>
                {property.area_m2 > 0 && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Preço/m²</span>
                    <span>R$ {(property.preco / property.area_m2).toFixed(0)}/m²</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}


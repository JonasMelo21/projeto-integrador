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
} from "lucide-react";
import { api, PropertyDetail } from "../services/api";
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Cell } from "recharts";

export function PropertyDetailsPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [property, setProperty] = useState<PropertyDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [isFavorite, setIsFavorite] = useState(false);

  useEffect(() => {
    const loadProperty = async () => {
      if (!id) {
        setError("ID do imóvel não fornecido");
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);
        const data = await api.getPropertyById(parseInt(id));
        if (!data) {
          setError("Imóvel não encontrado");
        } else {
          setProperty(data);
        }
      } catch (err) {
        setError("Falha ao carregar imóvel");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    loadProperty();
  }, [id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  if (error || !property) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <p className="text-destructive mb-4">{error}</p>
          <button
            onClick={() => navigate("/")}
            className="px-4 py-2 bg-primary text-primary-foreground rounded-lg"
          >
            Voltar para Imóveis
          </button>
        </div>
      </div>
    );
  }

  const priceData = [
    { name: "Mínimo", value: Math.max(2800, property.preco * 0.8) },
    { name: "Médio", value: Math.max(3500, property.preco * 0.95) },
    { name: "Este Imóvel", value: property.preco },
    { name: "Máximo", value: Math.max(4200, property.preco * 1.2) },
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
            <Heart
              className={`w-6 h-6 ${
                isFavorite ? "fill-red-500 text-red-500" : ""
              }`}
            />
          </button>
          <button className="p-2 hover:bg-secondary rounded-full transition-colors">
            <Share2 className="w-6 h-6" />
          </button>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 py-6 md:py-8">
        <div className="relative mb-6 rounded-2xl overflow-hidden">
          <div className="aspect-video md:aspect-[21/9] bg-muted relative">
            <img
              src={property.images[currentImageIndex]}
              alt={property.titulo}
              className="w-full h-full object-cover"
            />
            <div className="absolute top-4 left-4 px-3 py-1.5 rounded-full text-sm shadow-lg bg-success text-success-foreground">
              {property.preco < 3000 ? "Preço Justo" : "Oportunidade"}
            </div>
          </div>
          {property.images.length > 1 && (
            <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-2">
              {property.images.map((_, index) => (
                <button
                  key={index}
                  onClick={() => setCurrentImageIndex(index)}
                  className={`w-2 h-2 rounded-full transition-all ${
                    index === currentImageIndex
                      ? "bg-white w-6"
                      : "bg-white/50 hover:bg-white/75"
                  }`}
                />
              ))}
            </div>
          )}
        </div>

        <div className="grid md:grid-cols-3 gap-6 md:gap-8">
          <div className="md:col-span-2 space-y-6">
            <div>
              <h1 className="mb-2">{property.titulo}</h1>
              <div className="flex items-center gap-2 text-muted-foreground mb-4">
                <MapPin className="w-5 h-5" />
                <span>{property.local_bairro}, {property.local_cidade} - {property.local_uf}</span>
              </div>

              <div className="flex items-center gap-6 py-4 border-y border-border">
                <div className="flex items-center gap-2">
                  <Bed className="w-5 h-5 text-muted-foreground" />
                  <span>{property.quartos} quartos</span>
                </div>
                <div className="flex items-center gap-2">
                  <Bath className="w-5 h-5 text-muted-foreground" />
                  <span>{property.banheiros} banheiros</span>
                </div>
                <div className="flex items-center gap-2">
                  <Maximize className="w-5 h-5 text-muted-foreground" />
                  <span>{property.area_m2}m²</span>
                </div>
              </div>
            </div>

            <div>
              <h3 className="mb-3">Descrição</h3>
              <p className="text-muted-foreground leading-relaxed">
                {property.descricao}
              </p>
            </div>

            <div className="bg-card border border-border rounded-xl p-6">
              <h3 className="mb-4">Análise de Preço</h3>
              <div className="mb-4">
                <p className="text-sm text-muted-foreground mb-2">
                  Comparação com a região:
                </p>
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
                          fill={
                            entry.name === "Este Imóvel"
                              ? "#0A2540"
                              : "#E8F0FE"
                          }
                        />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <p className="text-sm text-muted-foreground">
                {property.preco < 3000 ? (
                  <>
                    Este imóvel oferece excelente{" "}
                    <span className="text-success">custo-benefício</span> com preços
                    competitivos.
                  </>
                ) : (
                  <>
                    Este imóvel está com{" "}
                    <span className="text-foreground">preço dentro da média</span> do
                    mercado.
                  </>
                )}
              </p>
            </div>
          </div>

          <div className="md:col-span-1">
            <div className="sticky top-20 bg-card border border-border rounded-xl p-6 shadow-lg">
              <div className="mb-6">
                <p className="text-sm text-muted-foreground mb-1">
                  Valor do Aluguel
                </p>
                <p className="text-3xl text-primary mb-1">
                  R$ {property.preco.toLocaleString()}
                </p>
                <p className="text-sm text-muted-foreground">/mês</p>
              </div>

              <button className="w-full bg-primary text-primary-foreground py-3 rounded-lg hover:bg-primary/90 transition-all shadow-md hover:shadow-lg flex items-center justify-center gap-2 mb-3">
                <MessageCircle className="w-5 h-5" />
                <span>Falar com {property.imobiliaria_nome}</span>
              </button>

              <button className="w-full border border-border py-3 rounded-lg hover:bg-secondary transition-colors">
                Agendar Visita
              </button>

              <div className="mt-6 pt-6 border-t border-border space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Aluguel</span>
                  <span>R$ {property.preco.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Condomínio</span>
                  <span>R$ 450</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">IPTU</span>
                  <span>R$ 180</span>
                </div>
                <div className="flex justify-between pt-3 border-t border-border">
                  <span>Total</span>
                  <span className="text-primary">
                    R$ {(property.preco + 450 + 180).toLocaleString()}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

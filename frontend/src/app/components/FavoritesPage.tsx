import { Heart } from "lucide-react";
import { PropertyCard } from "./PropertyCard";
import { mockProperties } from "../data/mockData";

export function FavoritesPage() {
  const favoriteProperties = mockProperties.slice(0, 3);

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-7xl mx-auto px-4 py-6 md:py-8">
        <div className="flex items-center gap-3 mb-6">
          <Heart className="w-8 h-8 text-primary fill-primary" />
          <h1>Meus Favoritos</h1>
        </div>

        {favoriteProperties.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <Heart className="w-16 h-16 text-muted-foreground mb-4" />
            <h2 className="text-muted-foreground mb-2">
              Nenhum favorito ainda
            </h2>
            <p className="text-sm text-muted-foreground">
              Comece a favoritar imóveis que você gosta!
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 md:gap-6">
            {favoriteProperties.map((property) => (
              <PropertyCard key={property.id} property={property} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

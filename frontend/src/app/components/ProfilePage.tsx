import { User, Mail, Phone, MapPin, Settings, LogOut, Bell, Shield } from "lucide-react";

export function ProfilePage() {
  const menuItems = [
    { icon: Settings, label: "Configurações", description: "Preferências gerais" },
    { icon: Bell, label: "Notificações", description: "Gerenciar alertas" },
    { icon: Shield, label: "Privacidade", description: "Segurança da conta" },
  ];

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-4xl mx-auto px-4 py-6 md:py-8">
        <div className="bg-card border border-border rounded-2xl overflow-hidden mb-6">
          <div className="h-32 bg-gradient-to-r from-primary to-primary/80"></div>
          <div className="px-6 pb-6">
            <div className="flex flex-col md:flex-row md:items-end gap-4 -mt-16">
              <div className="w-32 h-32 bg-white border-4 border-card rounded-full flex items-center justify-center shadow-lg">
                <User className="w-16 h-16 text-primary" />
              </div>
              <div className="flex-1 md:mb-4">
                <h1 className="mb-1">João Silva</h1>
                <p className="text-muted-foreground">Membro desde março de 2026</p>
              </div>
              <button className="md:mb-4 px-6 py-2 border border-border rounded-lg hover:bg-secondary transition-colors">
                Editar Perfil
              </button>
            </div>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-6 mb-6">
          <div className="bg-card border border-border rounded-xl p-6">
            <h3 className="mb-4">Informações de Contato</h3>
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-secondary rounded-full flex items-center justify-center">
                  <Mail className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Email</p>
                  <p>joao.silva@email.com</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-secondary rounded-full flex items-center justify-center">
                  <Phone className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Telefone</p>
                  <p>(11) 99999-9999</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-secondary rounded-full flex items-center justify-center">
                  <MapPin className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Localização</p>
                  <p>São Paulo, SP</p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-card border border-border rounded-xl p-6">
            <h3 className="mb-4">Estatísticas</h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-muted-foreground">Imóveis Favoritos</span>
                <span className="text-2xl text-primary">12</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-muted-foreground">Buscas Realizadas</span>
                <span className="text-2xl text-primary">47</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-muted-foreground">Visitas Agendadas</span>
                <span className="text-2xl text-primary">3</span>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-card border border-border rounded-xl overflow-hidden mb-6">
          {menuItems.map((item, index) => {
            const Icon = item.icon;
            return (
              <button
                key={index}
                className="w-full flex items-center gap-4 p-4 hover:bg-secondary transition-colors border-b border-border last:border-b-0"
              >
                <div className="w-12 h-12 bg-secondary rounded-full flex items-center justify-center">
                  <Icon className="w-6 h-6 text-primary" />
                </div>
                <div className="flex-1 text-left">
                  <p>{item.label}</p>
                  <p className="text-sm text-muted-foreground">
                    {item.description}
                  </p>
                </div>
                <div className="text-muted-foreground">›</div>
              </button>
            );
          })}
        </div>

        <button className="w-full flex items-center justify-center gap-3 p-4 border border-destructive text-destructive rounded-xl hover:bg-destructive hover:text-destructive-foreground transition-all">
          <LogOut className="w-5 h-5" />
          <span>Sair da Conta</span>
        </button>
      </div>
    </div>
  );
}

import { useState } from "react";
import { Send, Sparkles } from "lucide-react";

interface Message {
  id: string;
  text: string;
  sender: "user" | "ai";
  timestamp: Date;
}

export function ChatAIPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      text: "Olá! Sou seu assistente de imóveis com IA. Como posso ajudar você hoje?",
      sender: "ai",
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState("");

  const suggestedPrompts = [
    "Qual a média de aluguel em Pinheiros?",
    "Mostre imóveis com 2 quartos até R$ 3.000",
    "Quais bairros têm melhor custo-benefício?",
    "Compare preços de Studios no centro",
  ];

  const handleSendMessage = (text?: string) => {
    const messageText = text || inputValue.trim();
    if (!messageText) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: messageText,
      sender: "user",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");

    setTimeout(() => {
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: getAIResponse(messageText),
        sender: "ai",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiMessage]);
    }, 1000);
  };

  const getAIResponse = (query: string): string => {
    if (query.toLowerCase().includes("média") && query.toLowerCase().includes("pinheiros")) {
      return "A média de aluguel em Pinheiros é de R$ 3.200 para apartamentos de 2 quartos. Os preços variam entre R$ 2.500 e R$ 4.500, dependendo da localização e comodidades.";
    }
    if (query.toLowerCase().includes("2 quartos")) {
      return "Encontrei 12 imóveis com 2 quartos até R$ 3.000. Os bairros com melhor custo-benefício são: Consolação, Bela Vista e República. Gostaria de ver os resultados?";
    }
    if (query.toLowerCase().includes("custo-benefício")) {
      return "Com base na análise de Machine Learning, os bairros com melhor custo-benefício atualmente são: 1) Vila Madalena (-15% abaixo da média), 2) Bela Vista (-8%), 3) Moema (-5%). Estes bairros oferecem boa infraestrutura com preços competitivos.";
    }
    if (query.toLowerCase().includes("studios")) {
      return "Studios no centro variam entre R$ 1.600 e R$ 2.800. A República tem os preços mais acessíveis (média R$ 1.900), enquanto a Consolação tem média de R$ 2.400. Todos com ótima localização e acesso ao transporte público.";
    }
    return "Entendi sua pergunta. Estou analisando os dados do mercado imobiliário para fornecer a melhor resposta. Posso ajudar com informações sobre preços, bairros, comparações e recomendações personalizadas.";
  };

  return (
    <div className="h-full flex flex-col bg-background">
      <div className="bg-card border-b border-border px-4 py-4 md:px-6">
        <div className="max-w-4xl mx-auto flex items-center gap-3">
          <div className="w-10 h-10 bg-primary rounded-full flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-primary-foreground" />
          </div>
          <div>
            <h2 className="text-foreground">Assistente IA</h2>
            <p className="text-sm text-muted-foreground">
              Analise de mercado com Machine Learning
            </p>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-6 md:px-6">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.length === 1 && (
            <div className="mb-6">
              <p className="text-sm text-muted-foreground mb-4 text-center">
                Sugestões de perguntas:
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {suggestedPrompts.map((prompt, index) => (
                  <button
                    key={index}
                    onClick={() => handleSendMessage(prompt)}
                    className="p-4 border border-border rounded-xl hover:bg-secondary transition-all text-left text-sm"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${
                message.sender === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-[80%] md:max-w-[70%] rounded-2xl px-4 py-3 ${
                  message.sender === "user"
                    ? "bg-primary text-primary-foreground"
                    : "bg-card border border-border"
                }`}
              >
                {message.sender === "ai" && (
                  <div className="flex items-center gap-2 mb-2">
                    <Sparkles className="w-4 h-4 text-primary" />
                    <span className="text-xs text-muted-foreground">
                      Assistente IA
                    </span>
                  </div>
                )}
                <p className="text-sm leading-relaxed">{message.text}</p>
                <p
                  className={`text-xs mt-2 ${
                    message.sender === "user"
                      ? "text-primary-foreground/70"
                      : "text-muted-foreground"
                  }`}
                >
                  {message.timestamp.toLocaleTimeString("pt-BR", {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-card border-t border-border px-4 py-4 md:px-6">
        <div className="max-w-4xl mx-auto">
          <div className="flex gap-3">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
              placeholder="Digite sua pergunta sobre imóveis..."
              className="flex-1 px-4 py-3 border border-border rounded-xl bg-input-background focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
            />
            <button
              onClick={() => handleSendMessage()}
              disabled={!inputValue.trim()}
              className="px-6 py-3 bg-primary text-primary-foreground rounded-xl hover:bg-primary/90 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <Send className="w-5 h-5" />
              <span className="hidden md:inline">Enviar</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

import { useState, useRef, useEffect } from "react";
import { Send, Sparkles, Loader2 } from "lucide-react";

const VANNA_SSE_URL = "http://localhost:8000/api/vanna/v2/chat_sse";

interface Message {
  id: string;
  text: string;
  sender: "user" | "ai";
  timestamp: Date;
  loading?: boolean;
}

async function askVanna(
  question: string,
  conversationId: string,
  onChunk: (text: string) => void,
  onDone: () => void,
  onError: (msg: string) => void
) {
  try {
    const res = await fetch(VANNA_SSE_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: question, conversation_id: conversationId }),
    });

    if (!res.ok || !res.body) {
      onError(`Erro ${res.status}: não foi possível conectar ao backend.`);
      return;
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let accumulated = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value, { stream: true });
      // SSE lines: "data: <json>\n\n"
      const lines = chunk.split("\n");
      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;
        const raw = line.slice(6).trim();
        if (!raw || raw === "[DONE]") continue;
        try {
          const evt = JSON.parse(raw);
          // Vanna streams different component types; extract text content
          const text =
            evt.text ??
            evt.content ??
            evt.message ??
            (typeof evt === "string" ? evt : null);
          if (text) {
            accumulated += text;
            onChunk(accumulated);
          }
        } catch {
          // non-JSON line, skip
        }
      }
    }

    if (!accumulated) {
      onError("O assistente não retornou resposta. Verifique se o backend está rodando.");
    } else {
      onDone();
    }
  } catch (err) {
    onError("Não foi possível conectar ao backend (localhost:8000). Verifique se o servidor está rodando.");
  }
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
  const [isLoading, setIsLoading] = useState(false);
  const conversationId = useRef(`conv-${Date.now()}`);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const suggestedPrompts = [
    "Qual a média de preço por bairro?",
    "Mostre imóveis com 2 quartos até R$ 3.000",
    "Quais bairros têm melhor custo-benefício?",
    "Quantos imóveis existem por número de quartos?",
  ];

  const handleSendMessage = (text?: string) => {
    const messageText = text || inputValue.trim();
    if (!messageText || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: messageText,
      sender: "user",
      timestamp: new Date(),
    };

    const aiPlaceholderId = (Date.now() + 1).toString();
    const aiPlaceholder: Message = {
      id: aiPlaceholderId,
      text: "",
      sender: "ai",
      timestamp: new Date(),
      loading: true,
    };

    setMessages((prev) => [...prev, userMessage, aiPlaceholder]);
    setInputValue("");
    setIsLoading(true);

    askVanna(
      messageText,
      conversationId.current,
      (accumulated) => {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === aiPlaceholderId ? { ...m, text: accumulated, loading: true } : m
          )
        );
      },
      () => {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === aiPlaceholderId ? { ...m, loading: false } : m
          )
        );
        setIsLoading(false);
      },
      (errMsg) => {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === aiPlaceholderId
              ? { ...m, text: errMsg, loading: false }
              : m
          )
        );
        setIsLoading(false);
      }
    );
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
              Análise de mercado com Text-to-SQL
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
                {message.loading && !message.text ? (
                  <Loader2 className="w-4 h-4 animate-spin text-muted-foreground" />
                ) : (
                  <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.text}</p>
                )}
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
          <div ref={messagesEndRef} />
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
              disabled={isLoading}
              className="flex-1 px-4 py-3 border border-border rounded-xl bg-input-background focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all disabled:opacity-60"
            />
            <button
              onClick={() => handleSendMessage()}
              disabled={!inputValue.trim() || isLoading}
              className="px-6 py-3 bg-primary text-primary-foreground rounded-xl hover:bg-primary/90 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
              <span className="hidden md:inline">Enviar</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

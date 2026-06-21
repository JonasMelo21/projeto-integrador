import { useEffect } from "react";

// TypeScript declaration for the Vanna web component
declare global {
  namespace JSX {
    interface IntrinsicElements {
      "vanna-chat": React.DetailedHTMLProps<
        React.HTMLAttributes<HTMLElement>,
        HTMLElement
      > & {
        "api-base"?: string;
        "sse-endpoint"?: string;
        "ws-endpoint"?: string;
        "poll-endpoint"?: string;
      };
    }
  }
}

export function ChatAIPage() {
  useEffect(() => {
    if (!document.querySelector('script[src*="vanna-components"]')) {
      const script = document.createElement("script");
      script.type = "module";
      script.src = "https://img.vanna.ai/vanna-components.js";
      document.head.appendChild(script);
    }
  }, []);

  return (
    <div className="h-full w-full">
      <vanna-chat
        api-base="http://localhost:8000"
        sse-endpoint="http://localhost:8000/api/vanna/v2/chat_sse"
        ws-endpoint="http://localhost:8000/api/vanna/v2/chat_websocket"
        poll-endpoint="http://localhost:8000/api/vanna/v2/chat_poll"
        style={{ width: "100%", height: "100%", display: "block" }}
      />
    </div>
  );
}

"use client";

import { useState, useRef, useEffect } from "react";
import { sendMessage } from "@/lib/api";
import type { ChatMessage, AgentThought } from "@/lib/types";

function AgentThoughtChain({ thoughts }: { thoughts: AgentThought[] }) {
  const [expanded, setExpanded] = useState(false);
  if (!thoughts?.length) return null;

  const agentIcons: Record<string, string> = {
    router: "分流",
    knowledge: "知识库",
    tool: "工具",
    escalation: "升级",
    summary: "汇总",
  };

  return (
    <div className="mt-2 text-xs border border-zinc-200 rounded-lg overflow-hidden bg-zinc-50/50">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-2 w-full px-3 py-2 text-zinc-500 hover:text-zinc-700 transition-colors"
      >
        <span className="text-[10px] font-medium uppercase tracking-wider">Agent 处理过程</span>
        <span className="flex gap-1 ml-1">
          {thoughts.map((t, i) => (
            <span
              key={i}
              className={`inline-block w-1.5 h-1.5 rounded-full ${
                t.status === "completed" ? "bg-emerald-500" : t.status === "running" ? "bg-amber-400" : "bg-red-400"
              }`}
            />
          ))}
        </span>
        <span className="ml-auto text-zinc-400">{expanded ? "收起" : "展开"}</span>
      </button>
      {expanded && (
        <div className="border-t border-zinc-200 divide-y divide-zinc-100">
          {thoughts.map((t, i) => (
            <div key={i} className="px-3 py-2.5 space-y-1">
              <div className="flex items-center gap-2">
                <span className="font-medium text-zinc-700 text-[11px] bg-zinc-200/60 px-1.5 py-0.5 rounded">
                  {agentIcons[t.agent] || t.agent}
                </span>
                <span className={`text-[10px] px-1.5 py-0.5 rounded-full ${
                  t.status === "completed" ? "bg-emerald-50 text-emerald-600" : "bg-amber-50 text-amber-600"
                }`}>
                  {t.status}
                </span>
              </div>
              {t.detail && <div className="text-zinc-500 text-[11px] leading-relaxed">{t.detail}</div>}
              {t.output && (
                <div className="text-zinc-600 text-[11px] bg-white rounded px-2 py-1 border border-zinc-100">
                  {t.output}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function MessageBubble({ msg }: { msg: ChatMessage }) {
  const isUser = msg.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} animate-fade-in-up`}>
      <div className={`max-w-[80%] ${isUser ? "order-1" : "order-1"}`}>
        {!isUser && (
          <div className="flex items-center gap-2 mb-1.5">
            <div className="w-6 h-6 rounded-full bg-indigo-100 flex items-center justify-center text-[10px] font-bold text-indigo-600">
              AI
            </div>
            <span className="text-[11px] text-zinc-500 font-medium">电商智能客服</span>
          </div>
        )}
        <div
          className={`rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
            isUser
              ? "bg-indigo-600 text-white rounded-br-md"
              : "bg-white border border-zinc-200 rounded-bl-md shadow-sm"
          }`}
        >
          {msg.content}
        </div>
        {msg.thoughts && msg.thoughts.length > 0 && <AgentThoughtChain thoughts={msg.thoughts} />}
        {msg.ticket && (
          <div className="mt-2 p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs">
            <div className="font-medium text-amber-800 mb-1">工单已生成</div>
            <div className="text-amber-700 space-y-0.5">
              <div>编号：{msg.ticket.ticket_id}</div>
              <div>类别：{msg.ticket.issue_category}</div>
              <div>摘要：{msg.ticket.ticket_summary}</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function TypingIndicator() {
  return (
    <div className="flex justify-start animate-fade-in-up">
      <div className="max-w-[80%]">
        <div className="flex items-center gap-2 mb-1.5">
          <div className="w-6 h-6 rounded-full bg-indigo-100 flex items-center justify-center text-[10px] font-bold text-indigo-600">
            AI
          </div>
          <span className="text-[11px] text-zinc-500 font-medium">电商智能客服</span>
        </div>
        <div className="bg-white border border-zinc-200 rounded-2xl rounded-bl-md px-4 py-3 shadow-sm">
          <div className="flex gap-1.5">
            <span className="typing-dot w-2 h-2 bg-zinc-400 rounded-full inline-block" />
            <span className="typing-dot w-2 h-2 bg-zinc-400 rounded-full inline-block" />
            <span className="typing-dot w-2 h-2 bg-zinc-400 rounded-full inline-block" />
          </div>
        </div>
      </div>
    </div>
  );
}

export default function Home() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content: "你好！我是电商智能客服系统。我可以帮你查询产品信息、追踪订单、处理售后问题等。有什么可以帮你的？",
      thoughts: [],
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function handleSend() {
    const text = input.trim();
    if (!text || loading) return;

    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setLoading(true);

    try {
      const res = await sendMessage(text);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: res.reply,
          thoughts: res.thought_chain,
          ticket: res.escalation_ticket,
        },
      ]);
    } catch (e: unknown) {
      const errMsg = e instanceof Error ? e.message : "请求失败";
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `抱歉，处理时出了点问题：${errMsg}`,
          thoughts: [],
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col h-dvh max-w-3xl mx-auto w-full bg-white shadow-sm border-x border-zinc-200">
      {/* Header */}
      <div className="flex items-center gap-3 px-5 py-3 border-b border-zinc-200 bg-white shrink-0">
        <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white text-sm font-bold">
          A
        </div>
        <div>
          <h1 className="text-sm font-semibold text-zinc-900">电商智能客服系统</h1>
          <p className="text-[11px] text-zinc-500">LangGraph 多 Agent 系统</p>
        </div>
        <div className="ml-auto flex items-center gap-1.5 text-[11px] text-zinc-400">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
          在线
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4 bg-zinc-50/50">
        {messages.map((msg, i) => (
          <MessageBubble key={i} msg={msg} />
        ))}
        {loading && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="border-t border-zinc-200 bg-white px-4 py-3 shrink-0">
        <div className="flex items-end gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder="输入你的问题..."
            rows={1}
            className="flex-1 resize-none rounded-xl border border-zinc-300 bg-zinc-50 px-4 py-2.5 text-sm outline-none focus:border-indigo-500 focus:bg-white focus:ring-1 focus:ring-indigo-500/20 transition-all"
            disabled={loading}
          />
          <button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="shrink-0 h-10 w-10 rounded-xl bg-indigo-600 text-white flex items-center justify-center hover:bg-indigo-700 disabled:opacity-40 disabled:cursor-not-allowed transition-all active:scale-95"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M12 5l7 7-7 7" />
            </svg>
          </button>
        </div>
        <div className="mt-1.5 flex gap-3 text-[10px] text-zinc-400">
          <span>Enter 发送</span>
          <span>Shift+Enter 换行</span>
          <span className="ml-auto">示例：查询产品 / 追踪订单 / 退货政策</span>
        </div>
      </div>
    </div>
  );
}

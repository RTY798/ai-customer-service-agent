"""
电商智能客服系统 — CLI 交互模式

用法:
    python -m app.cli

命令:
    /help    显示帮助
    /quit    退出
"""

import sys
from app.agents.graph import agent_graph


BANNER = """
╔══════════════════════════════════════════╗
║       电商智能客服系统  v1.0              ║
║   LangGraph 多 Agent 智能客服             ║
║                                          ║
║   输入 /help 查看命令                     ║
║   输入 /quit 退出                         ║
╚══════════════════════════════════════════╝
"""


def main():
    print(BANNER)

    while True:
        try:
            user_input = input("  You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  再见！")
            break

        if not user_input:
            continue
        if user_input == "/quit":
            print("  再见！")
            break
        if user_input == "/help":
            print("  ── 可用命令 ──")
            print("  /quit         退出程序")
            print("  /help         显示帮助")
            print("  ── 使用提示 ──")
            print("  直接输入问题即可开始对话")
            print("  示例: \"查询订单 ORD-001\"")
            print("  示例: \"你们有什么产品？\"")
            print("  示例: \"我要投诉\"")
            print()
            continue

        result = agent_graph.invoke({
            "user_message": user_input,
            "messages": [],
            "thought_chain": [],
            "retrieved_docs": [],
            "tool_results": [],
        })

        reply = result.get("final_response", "")
        print(f"\n  Agent: {reply}")
        print()

        ticket = result.get("escalation_ticket")
        if ticket:
            print(f"  ┌─ 工单已生成 ─────────────────────")
            print(f"  │ 编号: {ticket['ticket_id']}")
            print(f"  │ 类别: {ticket.get('issue_category', '')}")
            print(f"  │ 摘要: {ticket.get('ticket_summary', '')}")
            print(f"  └──────────────────────────────────")
            print()

        # 显示思维链摘要
        thoughts = result.get("thought_chain", [])
        if thoughts:
            print(f"  [处理过程] {' → '.join(t['agent'] for t in thoughts)}")
            for t in thoughts:
                out = t.get("output", "")
                if out and len(str(out)) > 5:
                    print(f"    ▸ {t['agent']}: {out[:100]}")
            print()


if __name__ == "__main__":
    main()

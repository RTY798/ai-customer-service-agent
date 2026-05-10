"""初始化知识库和模拟数据"""
from app.knowledge_base.loader import seed_knowledge_base

if __name__ == "__main__":
    seed_knowledge_base()
    print("初始化完成！")

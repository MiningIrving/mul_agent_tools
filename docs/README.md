# Multi-Agent Financial Analysis Framework

基于 LangGraph 的状态驱动多智能体金融分析框架

## 项目概述

本项目是一个先进的金融分析系统，采用状态驱动的图形化工作流，通过多个专业化智能体协同工作，为用户提供全面的金融分析服务。

### 核心特性

- **状态驱动架构**: 使用 LangGraph 构建的动态工作流
- **多智能体协作**: 6个专业化智能体，各司其职
- **智能路由**: 自动识别查询复杂度并选择处理路径
- **错误恢复**: 完善的容错机制和自动重试逻辑
- **可观测性**: 集成 Langfuse 进行系统监控和调试

## 系统架构

### 核心组件

#### 1. GraphState (状态对象)
系统的"工作记忆"，包含：
- `original_query`: 用户原始查询
- `query_complexity`: 查询复杂度分类
- `task_plan`: 任务执行计划
- `agent_results`: 智能体执行结果
- `error_log`: 错误记录
- `final_answer`: 最终答案

#### 2. 图节点 (Graph Nodes)

| 节点 | 功能 | 说明 |
|------|------|------|
| Router | 查询分类 | 将查询分为 SIMPLE/COMPLEX/OOS |
| Planner | 任务规划 | 将复杂查询分解为子任务 |
| Agent Executor | 任务执行 | 动态调度智能体执行任务 |
| Remediation | 错误处理 | 智能错误恢复和重试 |
| Answer Generator | 答案合成 | 生成最终用户回复 |
| Fallback | 兜底处理 | 处理超出范围的查询 |

#### 3. 智能体 (Agents)

| 智能体 | 专长领域 | 可用工具 |
|--------|----------|----------|
| 选股agent | 股票筛选 | 个股信息查询、条件选股 |
| 新闻agent | 资讯收集 | 新闻查询、公告查询、研报查询 |
| 知识库agent | 知识教育 | 金融知识查询 |
| 诊股agent | 股票诊断 | 个股信息、新闻、公告、研报 |
| 预测agent | 趋势预测 | 个股信息查询、研报查询 |
| 荐股agent | 投资建议 | 所有工具 |

#### 4. 工具 (Tools)

| 工具 | 功能 | 说明 |
|------|------|------|
| 个股信息查询 | 获取股票基本信息 | 股价、财务指标、市场表现 |
| 条件选股 | 股票筛选 | 基于财务指标筛选股票 |
| 新闻查询 | 金融新闻 | 公司、行业、市场新闻 |
| 公告查询 | 公司公告 | 财报、重大事项、股东大会 |
| 研报查询 | 研究报告 | 券商研报、分析师观点 |
| 金融知识查询 | 知识教育 | 金融概念、投资策略解释 |

## 快速开始

### 安装

```bash
# 克隆项目
git clone https://github.com/MiningIrving/mul_agent_tools.git
cd mul_agent_tools

# 安装依赖
pip install -r requirements.txt

# 或者安装开发版本
pip install -e .
```

### 基本使用

```python
from src import FinancialAnalysisGraph

# 初始化系统
graph = FinancialAnalysisGraph()

# 执行查询
result = graph.invoke(
    query="比亚迪和特斯拉的财务表现对比分析",
    session_id="user_123"
)

print(result.final_answer)
```

### 配置

```python
# 启用持久化
graph = FinancialAnalysisGraph(enable_persistence=True)

# 集成 Langfuse
config = {
    "callbacks": [langfuse_handler],
    "configurable": {"thread_id": "session_123"}
}

result = graph.invoke(query, session_id, config=config)
```

## 使用示例

### 1. 简单查询
```
用户: "苹果公司的股价是多少？"
系统: 直接调用个股信息查询工具，返回实时股价信息
```

### 2. 复杂查询
```
用户: "筛选出市盈率低于20的科技股，并分析其中前3名的投资价值"

执行流程:
1. Router: 识别为 COMPLEX 查询
2. Planner: 分解为筛选任务 + 分析任务
3. Agent Executor: 
   - 选股agent 执行条件筛选
   - 诊股agent 分析前3名股票
4. Answer Generator: 合成综合分析报告
```

### 3. 知识查询
```
用户: "什么是市盈率？如何使用？"
系统: 知识库agent 提供详细解释、计算公式、应用实例
```

## 高级功能

### 错误处理与恢复

系统具备完善的错误处理机制：

```python
# 自动重试策略
if error_type in ["API_TIMEOUT", "NETWORK_ERROR"] and retry_count < 3:
    action = "retry"
elif error_type == "INVALID_STOCK_CODE":
    action = "replan"  # 重新规划任务
```

### 状态持久化

```python
# 启用状态持久化，支持中断恢复
graph = FinancialAnalysisGraph(enable_persistence=True)

# 流式处理，实时监控执行状态
for update in graph.stream(query, session_id):
    print(f"当前状态: {update}")
```

### 可观测性

集成 Langfuse 进行系统监控：

```python
from langfuse.callback import CallbackHandler

langfuse_handler = CallbackHandler(
    public_key="your_public_key",
    secret_key="your_secret_key"
)

config = {"callbacks": [langfuse_handler]}
result = graph.invoke(query, session_id, config=config)
```

## 开发指南

### 添加新的智能体

```python
from src.agents.base import BaseAgent

class CustomAgent(BaseAgent):
    def __init__(self, name: str):
        super().__init__(name)
        self.available_tools = ["tool1", "tool2"]
    
    def execute_task(self, state: GraphState, task: TaskDefinition):
        # 实现任务执行逻辑
        pass
    
    def get_available_tools(self):
        return self.available_tools
```

### 添加新的工具

```python
from src.tools.base import BaseTool

class CustomTool(BaseTool):
    def execute(self, **kwargs):
        # 实现工具功能
        pass
    
    def get_schema(self):
        # 返回输入参数的 JSON Schema
        pass
    
    def get_description(self):
        return "工具功能描述"
```

### 测试

```bash
# 运行测试
pytest tests/

# 运行特定测试
pytest tests/test_agents.py

# 生成覆盖率报告
pytest --cov=src tests/
```

## 性能优化

### 1. 模型选择
- Router 使用 GPT-3.5 快速分类
- Planner 使用 GPT-4 确保规划质量
- 其他节点根据需要选择合适模型

### 2. 缓存策略
```python
# 缓存常用查询结果
@lru_cache(maxsize=100)
def cached_stock_info(stock_code: str):
    return fetch_stock_data(stock_code)
```

### 3. 并发处理
```python
# 并行执行独立任务
import asyncio

async def parallel_execution(tasks):
    results = await asyncio.gather(*tasks)
    return results
```

## 部署建议

### 1. 环境变量配置
```bash
export OPENAI_API_KEY="your_openai_key"
export LANGFUSE_PUBLIC_KEY="your_langfuse_public_key"
export LANGFUSE_SECRET_KEY="your_langfuse_secret_key"
```

### 2. Docker 部署
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
CMD ["python", "-m", "src.main"]
```

### 3. 生产环境考虑
- 使用专业的 LLM 服务提供商
- 配置负载均衡和服务发现
- 实施监控和告警机制
- 定期备份状态数据

## 故障排除

### 常见问题

1. **LLM API 调用失败**
   - 检查 API 密钥配置
   - 确认网络连接
   - 查看速率限制

2. **状态持久化问题**
   - 检查存储权限
   - 验证序列化兼容性

3. **智能体执行超时**
   - 调整超时配置
   - 优化工具实现

### 调试技巧

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 检查图结构
print(graph.get_graph_visualization())

# 查看状态变化
for update in graph.stream(query, session_id):
    print(f"状态更新: {update}")
```

## 贡献指南

1. Fork 项目仓库
2. 创建功能分支: `git checkout -b feature/new-feature`
3. 提交更改: `git commit -am 'Add new feature'`
4. 推送分支: `git push origin feature/new-feature`
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 联系方式

- 作者: MiningIrving
- 项目地址: https://github.com/MiningIrving/mul_agent_tools
- 问题反馈: https://github.com/MiningIrving/mul_agent_tools/issues

## 致谢

感谢 LangGraph、LangChain 和 Langfuse 等开源项目为本框架提供的技术支持。
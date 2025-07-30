# API Reference

## Core Classes

### GraphState

The central state object that flows through the entire workflow.

```python
class GraphState(BaseModel):
    original_query: str
    query_complexity: Optional[Literal["SIMPLE", "COMPLEX", "OOS"]] = None
    task_plan: List[TaskDefinition] = Field(default_factory=list)
    agent_results: Dict[str, Any] = Field(default_factory=dict)
    error_log: List[ErrorRecord] = Field(default_factory=list)
    final_answer: str = ""
    session_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
```

#### Methods

- `update_timestamp()`: Update the last modified timestamp
- `add_error(task_id, agent, tool, error_type, error_message, retry_count=0)`: Add an error record
- `get_task_by_id(task_id)`: Get a task definition by ID
- `get_pending_tasks()`: Get all pending tasks
- `mark_task_completed(task_id, result)`: Mark a task as completed
- `mark_task_failed(task_id)`: Mark a task as failed
- `has_critical_errors()`: Check for critical errors

### FinancialAnalysisGraph

Main graph class that orchestrates the financial analysis workflow.

```python
class FinancialAnalysisGraph:
    def __init__(self, enable_persistence: bool = True)
    def invoke(self, query: str, session_id: str, config: Dict[str, Any] = None) -> GraphState
    def stream(self, query: str, session_id: str, config: Dict[str, Any] = None)
    def get_graph_visualization(self) -> str
    def get_state_schema(self) -> Dict[str, Any]
```

## Agents

### BaseAgent

Base class for all agents.

```python
class BaseAgent(ABC):
    def __init__(self, name: str)
    @abstractmethod
    def execute_task(self, state: GraphState, task: TaskDefinition) -> Any
    @abstractmethod  
    def get_available_tools(self) -> list
    def validate_task(self, task: TaskDefinition) -> bool
    def prepare_inputs(self, state: GraphState, task: TaskDefinition) -> Dict[str, Any]
```

### StockSelectionAgent

Agent specialized in stock screening and selection.

**Available Tools:**
- 个股信息查询
- 条件选股

**Usage:**
```python
agent = StockSelectionAgent("选股agent")
result = agent.execute_task(state, task)
```

### NewsAgent

Agent specialized in financial news gathering.

**Available Tools:**
- 新闻查询
- 公告查询  
- 研报查询

### KnowledgeAgent

Agent specialized in financial knowledge and education.

**Available Tools:**
- 金融知识查询

### DiagnosisAgent

Agent specialized in comprehensive stock analysis.

**Available Tools:**
- 个股信息查询
- 新闻查询
- 公告查询
- 研报查询

### PredictionAgent

Agent specialized in stock price prediction and trend analysis.

**Available Tools:**
- 个股信息查询
- 研报查询

### RecommendationAgent

Agent providing comprehensive investment recommendations.

**Available Tools:**
- All tools (个股信息查询, 条件选股, 新闻查询, 公告查询, 研报查询, 金融知识查询)

## Tools

### BaseTool

Base class for all tools.

```python
class BaseTool(ABC):
    def __init__(self, name: str)
    @abstractmethod
    def execute(self, **kwargs) -> Any
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]
    @abstractmethod
    def get_description(self) -> str
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool
```

### StockInfoTool

Tool for querying individual stock information.

**Parameters:**
- `stock_code` (str): Stock code (e.g., 000001.SZ, AAPL)
- `stock_name` (str): Company name
- `symbol` (str): Stock symbol
- `fields` (array, optional): Specific fields to retrieve

**Returns:** Dict with stock information including price, financial metrics, performance data.

### StockSelectionTool

Tool for conditional stock screening.

**Parameters:**
- `pe_ratio_max` (number): Maximum P/E ratio
- `pe_ratio_min` (number): Minimum P/E ratio  
- `pb_ratio_max` (number): Maximum P/B ratio
- `market_cap_min` (number): Minimum market cap
- `roe_min` (number): Minimum ROE
- `industry` (string): Industry filter
- `limit` (integer): Max results (default: 20)

**Returns:** List of stocks matching criteria.

### NewsQueryTool

Tool for querying financial news.

**Parameters:**
- `query` (string): Search query
- `company` (string): Company name or code
- `keywords` (array): Keywords to search
- `date_from` (string): Start date (YYYY-MM-DD)
- `date_to` (string): End date (YYYY-MM-DD)
- `limit` (integer): Max news items (default: 10)

**Returns:** List of news articles.

### AnnouncementTool

Tool for querying company announcements.

**Parameters:**
- `company` (string): Company name or stock code
- `announcement_type` (string): Type (财报, 重大事项, 股东大会, etc.)
- `date_from` (string): Start date
- `date_to` (string): End date
- `limit` (integer): Max announcements (default: 10)

**Returns:** List of company announcements.

### ResearchReportTool

Tool for querying analyst research reports.

**Parameters:**
- `company` (string): Company name or stock code
- `report_type` (string): Type (首次覆盖, 深度研究, 业绩点评, etc.)
- `rating` (string): Analyst rating filter
- `analyst_firm` (string): Research firm
- `limit` (integer): Max reports (default: 10)

**Returns:** List of research reports.

### KnowledgeQueryTool

Tool for querying financial knowledge.

**Parameters:**
- `query` (string): Knowledge query or concept
- `category` (string): Category filter (基础概念, 投资策略, etc.)
- `detail_level` (string): Detail level (基础, 中级, 高级)

**Returns:** Knowledge content with explanations, examples, and learning suggestions.

## Nodes

### router_node

Classifies queries into SIMPLE, COMPLEX, or OOS categories.

### planner_node

Decomposes complex queries into structured task plans using LLM function calling.

### agent_executor_node

Executes tasks from the task plan by dispatching to appropriate agents.

### remediation_node

Handles errors and makes intelligent recovery decisions.

### answer_generator_node  

Synthesizes final responses from all collected information.

### fallback_node

Handles out-of-scope queries with helpful responses.

## Utility Functions

### Agent Registry

```python
from src.agents import get_agent, list_available_agents

# Get agent by name
agent = get_agent("选股agent")

# List all available agents
agents = list_available_agents()
```

### Tool Registry

```python
from src.tools import get_tool, list_available_tools

# Get tool by name  
tool = get_tool("个股信息查询")

# List all available tools
tools = list_available_tools()
```

## Error Handling

### ErrorRecord

```python
class ErrorRecord(BaseModel):
    task_id: str
    agent: str
    tool: str
    error_type: str
    error_message: str
    timestamp: datetime
    retry_count: int = 0
```

### Common Error Types

- `API_TIMEOUT`: API request timeout
- `NETWORK_ERROR`: Network connectivity issues
- `INVALID_INPUT`: Invalid input parameters
- `AGENT_ERROR`: Agent execution failure
- `LLM_ERROR`: LLM response issues
- `UNRECOVERABLE_ERROR`: Critical failures

## Configuration

### Environment Variables

```bash
export OPENAI_API_KEY="your_openai_key"
export LANGFUSE_PUBLIC_KEY="your_langfuse_public_key"  
export LANGFUSE_SECRET_KEY="your_langfuse_secret_key"
```

### Langfuse Integration

```python
from langfuse.callback import CallbackHandler

langfuse_handler = CallbackHandler(
    public_key="your_public_key",
    secret_key="your_secret_key",
    host="https://cloud.langfuse.com"
)

config = {"callbacks": [langfuse_handler]}
result = graph.invoke(query, session_id, config=config)
```
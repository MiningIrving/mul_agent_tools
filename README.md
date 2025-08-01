面向状态驱动的、多智能体金融分析框架的架构蓝图引言：从静态路由到动态编排当前范式及其局限性当前金融大模型应用的普遍范式是基于意图识别的路由系统。在该模型中，用户查询首先被一个分类器解析，然后被分发到预定义的、功能单一的智能体（Agent）或工具（Tool）。例如，一个查询“比亚迪的股价是多少？”会被路由到“个股信息查询”工具。这种方法对于处理简单、原子性的请求是有效的，但当面对需要多个步骤、涉及多个信息源的复杂查询时，其固有的局限性便暴露无遗。该模式的核心问题在于其**无状态（Stateless）**的本质。每个请求都被视为一个独立的事务，系统缺乏对先前操作的记忆、无法进行动态的后续规划，也无法实现智能体之间的协同推理。当用户提出“对比亚迪和特斯拉的估值，并找出最近影响他们股价的研报”这类复杂问题时，静态路由系统无法将其分解为一系列有序的子任务（如：查询比亚迪估值、查询特斯拉估值、查询比亚迪研报、查询特斯拉研报），更无法综合所有结果给出一个连贯的答案。这种架构上的限制导致系统无法处理现实世界中常见的、需要深度分析的金融问题，从而严重制约了其应用价值。架构的跃迁：拥抱状态驱动的图（Graph）要突破上述瓶颈，解决方案在于进行一次架构上的范式跃迁：从无状态的线性处理转向有状态的、基于图的动态编排。在此背景下，LangGraph不仅是一个技术选型，更代表了一种构建智能体工作流的全新思维模式。它将问题的解决过程从一个简单的“请求-响应”链条，转变为一个动态的、状态不断演进的流程图。这种新范式将整个复杂任务的处理过程建模为一个有向图，其中每个节点（Node）代表一个处理单元（如一个智能体或一个逻辑判断），而边（Edge）则代表了控制流的转换路径。最关键的是，一个全局的**状态（State）**对象在图中流动，它承载着从任务开始到结束的所有信息。这种设计使得系统能够记忆历史、动态规划、自我纠正，从而实现真正意义上的复杂任务处理。拟议设计的核心原则本设计文档提出的新架构建立在三大核心原则之上：显式状态管理（Explicit State Management）：引入一个中心化的、持久化的状态对象，作为整个工作流的“唯一事实来源”（Single Source of Truth）。所有节点都通过读取和更新这个状态对象来进行通信和协作。动态控制流（Dynamic Control Flow）：利用图中的条件边（Conditional Edges）来实现智能路由、动态规划和自我修复。系统可以根据当前状态（例如，任务是否成功、数据是否完备）来决定下一步走向何方，而不是遵循僵化的预设路径。关注点分离（Separation of Concerns）：明确区分高层级的任务规划、战术性的工具执行以及最终的答案生成。这种分层设计使得系统更加模块化，易于开发、测试和维护。本文档路线图本设计文档将系统性地阐述这一新架构的各个层面。首先将介绍作为系统基石的状态对象和图结构，然后深入探讨负责任务分发和规划的网关节点，接着是执行具体任务的智能体工作单元，并详细说明如何构建一个具备弹性和恢复能力的容错框架。随后，将讨论如何合成高质量的最终答案，并利用可观测性工具对系统进行监控和优化。最后，通过一个完整的端到端示例，直观展示该架构在处理复杂金融查询时的强大能力。第一部分：核心架构：基于LangGraph的状态驱动编排1.1 状态的中心地位：系统的“工作记忆”在所提出的架构中，状态（State）对象是整个系统最关键的组件。它并非仅仅是一个数据容器，而是承载着上下文、数据、指令和历史记录的生命线，在图的各个节点之间流动。将状态对象设计为系统的“工作记忆”，是实现高级智能行为的基础。为了保证数据在整个工作流中的完整性和一致性，建议使用Pydantic等数据验证库来定义一个全局的State类。这确保了每个节点在读取或写入状态时，都遵循预先定义的、类型安全的数据结构，从而极大地减少了因数据格式不匹配而导致的运行时错误。这种设计超越了简单的数据传递。它赋予了系统进行**元认知（Meta-cognition）**的能力。通过允许智能体检查存储在状态中的历史操作、执行结果甚至失败记录，系统可以对其自身的处理过程进行“反思”。例如，诊股agent在执行任务前，可以检查状态中新闻agent的执行结果。如果发现新闻agent刚刚检索到了关于该股票的重大利空消息，诊股agent的诊断逻辑就可以动态调整，输出一个更加谨慎的分析结论。这种深度的上下文感知能力在无状态的路由系统中是无法实现的，而它正是一个精心设计的状态对象所带来的直接优势。这使得系统从一个单纯的数据检索工具，提升为一个具备初步推理能力的分析引擎。1.2 表1：全局状态对象模式下表提供了全局状态对象GraphState的正式模式定义。这张表不仅是技术文档的一部分，更是一份技术契约。它精确定义了图中所有节点必须遵守的数据读写接口。这种接口的标准化使得系统高度模块化、易于独立测试。任何开发新智能体的工程师都能清楚地知道他们将接收到什么样的数据，以及他们的输出需要遵循何种格式。键 (Key)类型 (Type)描述 (Description)示例 (Example)original_querystr用户输入的、未经修改的原始查询。"对比亚迪和特斯拉的估值，并找出最近影响他们股价的研报。"query_complexityEnum('SIMPLE', 'COMPLEX', 'OOS')由主路由器（Master Router）对查询进行的分类。COMPLEXtask_planList由规划器（Planner）节点生成的、结构化的分步任务计划。[{'agent': '选股agent', 'inputs': {'name': '比亚迪'}},...]agent_resultsDict[str, Any]一个字典，用于存储成功的智能体/工具调用输出，以唯一的任务ID作为键。{'task_1_output': {'pe_ratio': 25.3,...}}error_logList一个结构化的日志，记录执行过程中遇到的任何错误。``final_answerstr由答案生成智能体（Answer Generation Agent）合成的、面向用户的最终回复。"" (初始为空)session_idstr整个交互过程的唯一标识符，对于使用Langfuse进行追踪至关重要。"user123_session_abc"1.3 编排图：控制流的可视化本节将描述StatefulGraph的宏观结构。该图由一系列核心节点构成，主要包括：Router（路由器）、Planner（规划器）、Agent_Executor（智能体执行器）、Remediation（修复器）和Answer_Generator（答案生成器）。系统的智能决策能力主要通过**条件边（Conditional Edges）**实现。这些边会在每个节点执行完毕后，检查State对象的内容，并据此决定工作流的下一个方向。例如，一条条件边可以实现如下逻辑：IF state.query_complexity == 'COMPLEX' THEN GOTO Planner ELSE GOTO Agent_Executor。图结构本身就是一种被固化的知识。节点与边的连接方式，代表了系统解决问题的内置策略。与使用大量if/else语句的传统脚本相比，图结构是声明性的、可被可视化的。它清晰地分离了“做什么”（节点的功能）和“如何做”（边的逻辑）。这种分离使得系统的业务逻辑极易理解、调试和修改。当出现新的业务需求时，通常只需增加一个新的节点和几条边，而无需重构庞大的单体脚本。这一架构选择直接关系到系统的长期可维护性。第二部分：网关：高级路由与动态任务规划2.1 “主路由器”节点：第一道防线“主路由器”（Master Router）节点是整个图的入口。其唯一职责是接收用户查询，通过一次大语言模型（LLM）调用，对查询的复杂性进行分类，并更新State对象中的query_complexity字段。为了实现准确的分类，需要对该节点的LLM提示词（Prompt）进行精心设计。提示词应包含清晰的指令和少量示例（Few-shot examples），以引导模型进行三元分类：SIMPLE（简单）：能够由单个工具或智能体直接回答的查询。例如：“茅台的市盈率是多少？”COMPLEX（复杂）：需要多个智能体协作、分步执行才能回答的查询。例如：“比较苹果和微软的财务状况，并总结它们各自的风险。”OOS（Out-of-Scope，超出范围）：与金融领域无关的查询。例如：“今天天气怎么样？”该节点的输出直接决定了图中的第一个主要分支：SIMPLE查询将绕过规划器，直接进入Agent_Executor；COMPLEX查询将被送往Planner进行任务分解；而OOS查询则直接流向兜底agent（Fallback Agent）进行礼貌性回复。2.2 “规划器”节点：利用Function Calling分解复杂性“规划器”（Planner）节点是处理复杂请求的核心。它仅在查询被分类为COMPLEX时被激活。该节点的核心技术是利用大语言模型的Function Calling能力，将宏大的用户意图分解为一系列具体的、可执行的子任务。具体实现上，可以定义一组专用于规划的“工具”，而不是直接执行的工具。例如，可以定义一个Pydantic类Task，它包含task_id、agent、tool、inputs等字段。然后定义一个名为create_execution_plan(tasks: List)的函数。LLM被指示，在理解用户复杂查询后，调用这个create_execution_plan函数，并传入一个由多个Task实例组成的列表。这个过程实现了规划推理与规划执行的至关重要的分离。规划器LLM可以是一个经过特别优化、擅长逻辑分解和结构化输出的模型，而后续执行任务的智能体则可以专注于工具调用和数据检索。这种职责分离允许为不同阶段选择最合适（可能更小、更快或更专业）的模型，从而优化系统整体的性能和成本。此外，规划器生成的task_plan是一个人类可读的结构化数据，可以被记录在Langfuse中。这使得调试系统“为什么”决定采取某一行动路径变得异常简单。规划器节点的输出是一个结构化的子任务列表，该列表将被写入State对象的task_plan字段中，供后续节点使用。2.3 分解过程示例用户查询：“筛选出市盈率低于20、市值超过1000亿美元的科技股。对于排名前三的结果，诊断它们近期的表现并总结相关新闻。”规划器的输出 (写入State.task_plan)：JSON[
  {
    "task_id": "task_1",
    "agent": "选股agent",
    "tool": "条件选股",
    "inputs": {"pe_ratio_max": 20, "market_cap_min": 100000000000, "industry": "科技"}
  },
  {
    "task_id": "task_2",
    "agent": "诊股agent",
    "tool": "诊股",
    "inputs": {"depends_on": "task_1", "stock_codes": "results[0:3]"}
  },
  {
    "task_id": "task_3",
    "agent": "新闻agent",
    "tool": "新闻查询",
    "inputs": {"depends_on": "task_1", "company_names": "results[0:3]"}
  }
]
这个示例清晰地展示了规划结果的结构化特性。它不仅定义了每个子任务由哪个智能体、使用哪个工具来执行，还通过depends_on字段明确了任务之间的依赖关系。这实际上将一个复杂的请求转换成了一个任务的有向无环图（DAG），为后续的有序执行提供了清晰的蓝图。第三部分：工作单元：专业化的智能体执行器3.1 “智能体执行器”节点：图的主力军“智能体执行器”（Agent Executor）节点是图中的核心工作单元。它并非一个单一功能的节点，而是一个动态的调度器。在一个循环结构中，Agent_Executor节点会从State.task_plan中读取下一个待处理的任务，根据任务定义识别出需要调用的智能体（例如诊股agent），然后调用该智能体来执行任务。为了实现这种调度，必须为所有智能体定义一个标准化的接口。每个智能体都应被实现为一个函数，该函数接收State对象和当前task的详细信息作为输入。智能体在其内部调用其拥有的工具来完成指定工作，并返回一个包含结果的字典。这个结果随后被添加到State.agent_results字典中，并以其task_id作为键。同时，该任务在State.task_plan中被标记为已完成。这个过程不断重复，直到所有任务都被执行完毕。3.2 表2：智能体-工具能力矩阵下方的矩阵清晰地展示了系统内部的劳动分工和权限划分。这张表格对于设计阶段的清晰度和实施阶段的安全性都至关重要。它能够有效防止“权限蔓延”——即某个智能体被意外地赋予了它本不应使用的工具。例如，荐股agent可能需要访问所有工具以进行全面分析，而知识库agent则应被严格限制在只能访问金融知识查询工具，以防止它无意中提供投资建议。该矩阵为实现这些访问控制提供了明确的规范。智能体 (Agent)个股信息查询条件选股新闻查询公告查询研报查询金融知识查询选股agent✅✅新闻agent✅✅✅知识库agent✅诊股agent✅✅✅✅预测agent✅✅荐股agent✅✅✅✅✅✅3.3 在LangGraph中建模循环遍历task_plan并逐一执行任务的过程，可以通过在LangGraph中构建一个循环来实现。这通常由一个条件边完成。在Agent_Executor节点执行完毕后，一条条件边会检查状态：“State.task_plan中是否还有待处理的任务？”如果是，该边将控制流导回Agent_Executor节点，以处理下一个任务。如果否，意味着所有任务已完成，该边将控制流导向下一个阶段，即Answer_Generator节点。这种基于图的循环比传统代码中的for循环更加健壮。由于LangGraph在每一步执行后都会保存状态，如果系统在一个包含10个步骤的复杂计划中途（例如在第5步之后）崩溃，它可以在恢复后直接从第6步开始执行，而无需重新运行前5个已经成功的步骤。对于执行时间较长的复杂任务，这是一个极其强大的特性，保证了任务的最终完成率。第四部分：弹性与恢复：一个容错框架4.1 主动错误捕获与状态日志记录为了构建一个具备弹性的系统，必须强制要求每个智能体内部的所有工具调用都被包裹在try-except代码块中。这是一个基础但至关重要的设计原则。关键在于，当捕获到一个异常时，它不应导致整个工作流的终止。相反，异常的详细信息（如错误消息、堆栈跟踪、相关的task_id）应被捕获，并作为一个结构化对象追加到State.error_log列表中。随后，该智能体应返回一个明确的失败信号，而不是结果数据。这种设计将错误从“进程杀手”转变成了可供决策的数据点。一个错误不再是灾难，而仅仅是状态中新增的一条信息。系统可以基于这条信息，做出智能的、有针对性的后续决策。这是构建能够自我修正的系统的基本前提。4.2 “修复器”节点：系统的免疫反应“修复器”（Remediation）是一个专用的条件路由节点，它在State.error_log被更新后（即发生错误时）被触发。它的作用类似于系统的免疫系统。该节点会检查State.error_log中的最新错误记录，并根据一组预定义的规则，决定下一步的行动方案。这种机制将错误处理从简单的、通用的“重试”逻辑，提升为一种复杂的、具备上下文感知的策略。例如，它能够区分是应该重试、是应该放弃当前子任务并继续、还是应该返回规划器重新规划路径。4.3 表3：修复器节点决策逻辑下表将修复器节点的智能决策过程进行了规则化。将这套逻辑以表格形式固化下来，而不是硬编码在代码中，可以提供一个清晰、可扩展的规则手册。当在系统运行中发现新的常见故障类型时（例如，某个API引入了新的速率限制），只需向该决策逻辑中添加一条新规则，而无需重写核心的图逻辑。错误类型 (从消息中推断)状态条件行动 (Action)下一节点API_TIMEOUT, NETWORK_ERRORretry_count < 3增加该任务的重试计数器。Agent_ExecutorINVALID_STOCK_CODElen(task_plan) > 1将任务标记为失败。记录一条笔记以通知规划器。Planner (进行重新规划)AGENT_HALLUCINATION (例如，工具输入格式错误)retry_count < 2使用更严格的提示词重新运行该智能体。Agent_ExecutorUNRECOVERABLE_ERROR (例如，认证失败)任何条件将任务标记为永久失败。Agent_Executor (继续执行其他任务)所有其他错误 / 达到最大重试次数任何条件将任务标记为永久失败。Agent_Executor (继续执行其他任务)4.4 “兜底agent”节点：终极安全网“兜底agent”（Fallback Agent）是系统的最后一道防线。它是两类查询的最终归宿：一类是被Router节点直接判定为OOS（超出范围）的查询；另一类是在执行复杂任务过程中遭遇了无法恢复的重大失败的工作流。该智能体的提示词需要经过精心设计，以体现出同理心和乐于助人的态度。它不能简单地回答“我无法回答”。一个优秀的兜底回复应该：明确告知用户系统的核心能力范围（例如：“我是一个专注于金融分析的AI助手”）。解释为什么无法回答当前问题（例如：“我无法提供天气预报”）。如果可能，建议用户如何重述问题以使其落在系统的能力范围内（例如：“您可以尝试询问关于上市公司或金融市场的问题”）。这种优雅的失败处理方式能够极大地提升用户体验，并有效管理用户预期。第五部分：合成器：生成高保真度的回复5.1 “回答agent”节点：从数据到叙事“回答agent”（Answer Generation Agent）是主成功路径中的最后一个节点。它的唯一目标是根据之前所有步骤收集到的信息，精心 crafting 出最终呈现给用户的回复。此节点的一个关键设计决策是，它接收**整个最终状态对象（final State object）**作为其输入，而不仅仅是agent_results中的数据。一个欠佳的设计可能会简单地将所有工具的原始输出拼接在一起。然而，通过传入完整的状态，可以解锁更高层次的综合能力。该智能体能够：看到original_query，从而深刻理解用户的真实意图。看到task_plan，从而了解为了回答问题都执行了哪些步骤。看到agent_results，从而获取所有成功检索到的数据。最关键的是，看到error_log，从而能够优雅地承认并说明哪些信息未能获取到。这种透明度允许生成类似这样的高质量回复：“根据您的要求，我对 比亚迪 和 特斯拉 进行了分析。我成功获取了它们的估值指标和近期新闻。但由于暂时的网络连接问题，我未能获取到最新的分析师研究报告。基于现有信息，我的综合分析如下...”。这种诚实和透明的沟通方式是建立用户信任的关键，也是一个真正先进的AI系统的标志。5.2 用于高质量合成的高级提示工程为了引导LLM生成结构清晰、内容丰富的回复，需要为回答agent设计一个高级的提示词模板。该模板应包含以下指令：设定角色（Adopt a Persona）：“你是一位来自顶级投资机构的资深金融分析师。”结构化回复（Structure the Response）：“首先提供一个高层次的执行摘要（TL;DR），然后进行详细的分点阐述，请使用Markdown格式以保证清晰度。”综合而非罗列（Synthesize, Don't List）：“不要仅仅罗列数据。请将来自不同来源的信息（如财务数据、新闻事件、公司公告）融合成一个连贯的叙事。例如，尝试将一个新闻事件与股价的变动联系起来。”注明来源（Cite Sources）：“当使用某条信息时，请提及它来自哪个工具或步骤（例如，‘根据最新的公司公告...’或‘财报数据显示...’）。”承认局限性（Acknowledge Limitations）：“请检查错误日志。如果有任何用户要求的信息未能获取，请清晰、礼貌地说明情况。”通过这样的提示词工程，可以确保最终输出给用户的不仅仅是冰冷的数据，而是一份有深度、有见解、有温度的专业分析报告。第六部分：系统可观测性：使用Langfuse进行调试与监控6.1 与LangGraph的无缝集成本节将提供将Langfuse集成到整个LangGraph应用的实用指南。技术上，这通常只需要在图的配置中添加Langfuse的回调处理器（Callback Handler）即可实现。集成的关键在于语义化命名。每个完整的用户查询处理流程都应该被记录为一个Langfuse的Trace，并以session_id进行命名。在图中的每一次节点执行（例如Planner、Agent_Executor的一次调用）都会自动成为该Trace下的一个Step。而在一个节点内部的每一次LLM调用或工具调用，则会成为一个嵌套的Span。这种自动形成的层级结构，使得整个复杂工作流在Langfuse的界面中变得一目了然、极易追溯。6.2 从调试到持续改进调试（Debugging）：当一个复杂的查询失败或返回了不理想的结果时，开发人员可以在Langfuse中找到对应的Trace。通过可视化的界面，他们可以逐层展开，检查每个Step和Span的输入、输出、耗时、Token消耗以及记录的任何错误。这使得定位多步链条中的故障点变得异常高效，从根本上改变了调试复杂AI系统的体验。然而，Langfuse的真正威力并不仅仅在于被动的调试，更在于主动的优化。当系统上线运行后，汇聚在Langfuse中的海量、结构化的追踪数据就成了一座金矿。团队可以基于这些数据构建仪表盘，以回答关键的业务和性能问题：性能分析：“诊股agent的P95延迟是多少？哪个工具调用是瓶颈？”成本控制：“Planner节点每天的Token消耗和API费用是多少？”质量评估：“哪些类型的用户查询获得了最低的用户评分？查看它们的Trace，找出失败的共性模式。”行为洞察：“Remediation节点被触发的频率有多高？最常见的原因是什么？”这种由数据驱动的反馈循环，使得团队能够超越猜测，开始进行有针对性的、高影响力的改进，无论是优化提示词、调整图的逻辑，还是增强某个智能体的能力。这是一个优秀的系统演变为一个卓越系统的必经之路。第七部分：实施演练：一个复杂查询的完整流程7.1 场景设定为了具体展示该架构的运作方式，将使用一个真实且全面的用户查询作为示例：“我正在考虑投资中国的新能源汽车行业。请比较比亚迪（002594.SZ）和蔚来（NIO）的关键财务指标（市盈率、市销率、负债权益比）。同时，查找两家公司近期关于供应链问题的相关新闻和分析师研报。基于以上所有信息，给出一个比较性的总结和展望。”7.2 状态在图中的旅程追踪以下将以叙事的方式，描述State对象在图的各个节点间流转时，其内部内容的变化过程：输入：用户查询进入系统。State对象被初始化，original_query字段被填充。Router 节点：LLM分析查询后，判定其为复杂任务。State.query_complexity被设置为COMPLEX。Planner 节点：Planner接收到查询后，通过Function Calling生成一个多步计划，并写入State.task_plan。该计划可能包含如下任务：task_1: 个股信息查询 for BYD (metrics)task_2: 个股信息查询 for NIO (metrics)task_3: 新闻查询 for BYD (supply chain)task_4: 新闻查询 for NIO (supply chain)task_5: 研报查询 for BYD (supply chain)task_6: 研报查询 for NIO (supply chain)Agent Executor 循环 (第1次迭代)：执行task_1。调用个股信息查询工具获取比亚迪的财务指标。结果被写入State.agent_results['task_1_output']。Agent Executor 循环 (第2次迭代)：执行task_2。获取蔚来的财务指标，并更新State.agent_results。... 依次执行：系统继续执行task_3和task_4，获取两家公司的新闻。模拟失败与修复：在执行task_6（查询蔚来研报）时，假设研报查询工具未能找到相关报告并返回了一个NotFound错误。该错误被捕获并写入State.error_log。控制流进入Remediation节点。根据决策逻辑（表3），NotFound错误被视为不可重试的失败。Remediation节点决定将该任务标记为失败，并让工作流继续执行剩余任务（如果有的话）。Answer Generator 节点：所有任务执行完毕后，控制流到达Answer_Generator。该节点接收到最终的State对象，其中包含了成功获取的比亚迪和蔚来的财务指标、新闻，以及一条关于未能找到蔚来研报的错误记录。输出：回答agent基于完整的State信息，生成一份全面的、结构化的分析报告。报告会首先对比各项财务数据和新闻，然后明确指出“未能找到关于蔚来供应链问题的近期研报”，最后给出一个综合的、平衡的总结与展望。这份高质量的答案最终被呈现给用户。7.3 关键代码片段 (Python伪代码)为了使设计更加具体，以下提供了一些说明性的代码片段，展示了核心组件的实现方式。1. 定义GraphStatePythonfrom typing import List, Dict, Any, Literal
from pydantic import BaseModel

class GraphState(BaseModel):
    original_query: str
    query_complexity: Literal = None
    task_plan: List] =
    agent_results: Dict[str, Any] = {}
    error_log: List] =
    final_answer: str = ""
    session_id: str
2. 智能体节点函数示例Pythondef stock_diagnosis_agent_node(state: GraphState, task: Dict) -> Dict:
    """
    一个诊股智能体节点的示例实现。
    它接收当前状态和任务详情，执行操作，并返回结果。
    """
    try:
        stock_code = task['inputs']['stock_code']
        # 假设 diagnosis_tool 是一个已经定义好的工具函数
        diagnosis_result = diagnosis_tool(stock_code=stock_code)
        
        # 返回成功的结果
        return {"result": diagnosis_result}
    except Exception as e:
        # 捕获异常，记录到error_log，并返回失败信号
        error_info = {
            "task_id": task['task_id'],
            "agent": "诊股agent",
            "error": str(e)
        }
        state['error_log'].append(error_info)
        return {"error": True}
3. 条件边逻辑示例Pythondef should_continue_loop(state: GraphState) -> Literal["continue", "end"]:
    """
    一个条件边的逻辑函数，决定是否继续执行任务循环。
    """
    pending_tasks = [
        task for task in state['task_plan'] 
        if task['task_id'] not in state['agent_results']
    
    if not pending_tasks:
        # 没有待处理任务，结束循环
        return "end"
    else:
        # 仍有待处理任务，继续循环
        return "continue"
4. Langfuse回调处理器集成Pythonfrom langfuse.callback import CallbackHandler
from langgraph.graph import StateGraph, END

# 初始化Langfuse处理器
langfuse_handler = CallbackHandler(
    public_key="YOUR_PUBLIC_KEY",
    secret_key="YOUR_SECRET_KEY",
    host="https://cloud.langfuse.com"
)

# 在构建图时传入回调
workflow = StateGraph(GraphState)
#... 添加节点和边...
app = workflow.compile(checkpointer=memory_saver)

# 在调用时传入配置
config = {"configurable": {"thread_id": "some_session_id"}, "callbacks": [langfuse_handler]}
response = app.invoke({"original_query": "...", "session_id": "some_session_id"}, config=config)
通过上述设计和示例，一个强大、健壮且可观测的金融AI分析框架的蓝图得以清晰呈现。该架构不仅解决了当前简单路由系统所面临的瓶颈，更为未来功能的扩展和系统智能的持续进化奠定了坚实的基础。

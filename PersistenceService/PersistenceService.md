# Persistence Service 产品与开发文档

## 1. 产品概述 (Product Overview)

### 1.1 职责 (Responsibility)
数据库服务 (Persistence Service) 是 Synapse 平台与 PostgreSQL 数据库交互的**唯一**网关。它封装了所有与数据库相关的操作，确保数据访问的一致性、安全性和可追踪性。

### 1.2 核心需求 (Core Requirements)
根据《系统模块说明.md》(FR-DB-xx)，本服务需满足以下核心需求：
*   **FR-DB-01**: 封装所有 SQL 的 CRUD 操作。
*   **FR-DB-02**: 管理数据库连接池和事务。
*   **FR-DB-03**: 能与 `task_history` 等版本化历史表进行交互。
*   **FR-DB-04**: 所有数据库查询**必须**在一个追踪 `Span` 内执行，并记录关键信息。

## 2. 开发计划 (Development Plan)

遵循《建议开发顺序.md》中的 M1 阶段目标，我们将分阶段实现 Persistence Service。

### 2.1 阶段一：核心骨架 (Milestone 1 - MVP)
目标：实现最基本的数据访问功能，支持“Hello World”工作流。

#### 2.1.1 核心功能开发 (Core Functionality)
*   **数据库连接与配置**:
    *   实现数据库连接池管理（使用 `psycopg2` 或 `asyncpg`）。
    *   从配置文件或环境变量读取数据库连接信息。
*   **基础数据模型映射**:
    *   定义与数据库表结构对应的 Python 数据类或 Pydantic 模型（例如 `TaskModel`, `EdgeModel`）。
    *   初期重点实现 `tasks` 和 `edges` 表的基本字段。
*   **CRUD 操作**:
    *   实现对 `tasks` 表的基本操作：
        *   `create_task(task_def: TaskDefinition) -> UUID`: 创建新任务。
        *   `get_task_by_id(task_id: UUID) -> Optional[TaskRecord]`: 根据 ID 获取任务。
        *   `update_task_status(task_id: UUID, status: str, result: Optional[Dict[str, Any]] = None)`: 更新任务状态和结果。
        *   `list_pending_tasks() -> List[TaskRecord]`: 查询所有待处理 (`PENDING`) 的任务（为简化版图引擎服务）。
    *   实现对 `edges` 表的基本查询操作：
        *   `get_outgoing_edges(task_id: UUID) -> List[EdgeRecord]`: 获取从指定任务出发的所有边。
    *   **JSONB 查询支持**:
        *   实现至少一个利用GIN索引对`input_data`或`result` JSONB字段进行键值查询的函数，例如 `find_tasks_by_result_property(key: str, value: Any) -> List[TaskRecord]`。这将在初期就验证我们对JSONB的依赖是可行的。
    *   **图/向量查询的占位符**:
        *   虽然初期不实现复杂的图/向量逻辑，但`repository`层应预留接口（Interface Placeholder），例如`find_related_tasks_by_graph(task_id: UUID)`和`find_similar_experiences_by_vector(vector: List[float])`。这能确保上层模块（如图引擎、上下文服务）可以先行开发，而无需等待底层图/向量查询的完整实现。
*   **事务管理**:
    *   提供简单的事务上下文管理器，用于保证相关操作的原子性（如创建任务和边）。
    *   **业务级事务**: 本服务提供的核心事务，是**业务级的**。例如，`create_workflow_from_blueprint(plan_blueprint: PlanBlueprint)`这个方法，其内部会将解析`PlanBlueprint`并创建所有`tasks`和`edges`的数据库操作，包裹在一个**单一的、原子性的数据库事务**中。这确保了工作流图的创建要么完全成功，要么完全失败，绝不会出现‘半成品’的状态。
*   **集成日志与追踪 (FR-DB-04)**:
    *   在关键操作（如查询、更新）前后添加日志记录。
    *   集成 `Logging & Tracing Service`，确保每个数据库操作都在一个追踪 `Span` 内执行。

#### 2.1.2 数据库表结构设计 (Initial DB Schema)
**注意**: 此表结构为初期简化版，后续会根据《系统模块说明.md》和《静态能力和蓝图json.md》进行扩展。

```sql
-- tasks 表 (MVP增强版)
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL,
    -- goal TEXT, -- goal可以被视为input_data的一部分
    assignee_id VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    input_data JSONB, -- 直接使用input_data
    result JSONB,
    directives JSONB, -- 即使初期不用，也最好预留
    parent_task_id UUID, -- 预留层级关系
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- edges 表 (MVP增强版)
CREATE TABLE edges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL,
    source_task_id UUID NOT NULL, -- 暂不加外键，简化初期开发
    target_task_id UUID NOT NULL,
    condition JSONB, -- 直接使用JSONB存储CEL
    data_flow JSONB, -- 预留数据流映射
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### 2.2 阶段二：功能增强 (Milestone 2 - Enhanced Features)
目标：支持更复杂的任务属性和数据交互。

#### 2.2.1 数据模型扩展
*   根据 `interfaces.py` 中的 `TaskDefinition`, `EdgeDefinition` 等模型，扩展数据库表字段和对应的 Python 模型。
*   添加对 `directives`, `context_overrides` 等复杂字段的支持。

#### 2.2.2 CRUD 操作增强
*   增加对 `edges` 表的创建和更新操作。
*   实现更复杂的查询，例如根据 `workflow_id` 获取整个工作流的拓扑结构。

### 2.3 阶段三：版本化支持 (Milestone 3 - Versioning Support)
目标：实现 FR-DB-03，支持任务历史版本。

#### 2.3.1 数据模型与表结构
*   设计并创建 `task_history` 表，用于存储任务的每次变更记录。
*   `task_history` 可能包含 `task_id`, `version_number`, `data_snapshot` (JSONB), `created_at` 等字段。

#### 2.3.2 CRUD 操作
*   实现对 `task_history` 表的写入操作（可能通过数据库触发器或应用层逻辑）。
*   提供查询历史记录的接口。

## 3. 技术选型 (Technology Stack)

*   **编程语言**: Python 3.11+
*   **数据库**: PostgreSQL
*   **ORM/驱动**: `psycopg2-binary` (同步) 或 `asyncpg` (异步，如果系统整体是异步的)
*   **连接池**: `psycopg2` 内置连接池 或 `SQLAlchemy` (如果使用 ORM)
*   **日志**: 集成项目统一的日志服务
*   **追踪**: 集成项目统一的追踪服务 (OpenTelemetry)

## 4. 模块结构 (Module Structure)

```
PersistenceService/
├── __init__.py
├── config.py             # 数据库配置
├── database.py           # 数据库连接池管理
├── models/               # 数据模型定义
│   ├── __init__.py
│   ├── task.py
│   ├── edge.py
│   └── ...
├── repository/           # 数据访问层 (Repository Pattern)
│   ├── __init__.py
│   ├── task_repository.py
│   ├── edge_repository.py
│   └── ...
├── service.py            # 核心服务接口 (供其他模块调用)
├── transaction.py        # 事务管理器
├── tracing.py            # 与追踪服务集成的辅助函数
├── tests/                # 单元测试
│   ├── __init__.py
│   ├── test_task_repository.py
│   └── ...
└── README.md             # 模块说明文档
```

## 5. API 接口示例 (API Interface Examples)

为确保模块间的强类型约束和契约驱动开发，`service.py` 的**所有**对外方法，其参数和返回值的类型注解，都**必须**严格使用从 `interfaces.py` 中导入的 Pydantic 模型。

```python
# service.py
from uuid import UUID
from typing import List, Optional
# 【核心】所有类型都来自统一的契约文件
from interfaces import TaskRecord, EdgeRecord, PlanBlueprint, TaskDefinition, EdgeDefinition

class PersistenceService:
    def create_task(self, task_def: TaskDefinition) -> UUID:
        """创建一个新任务"""
        pass

    def get_task(self, task_id: UUID) -> Optional[TaskRecord]:
        """根据ID获取任务"""
        pass

    def update_task_result(self, task_id: UUID, result: Dict[str, Any]) -> bool:
        """更新任务执行结果"""
        pass

    def list_pending_tasks(self) -> List[TaskRecord]:
        """列出所有待处理的任务"""
        pass

    def get_outgoing_edges(self, task_id: UUID) -> List[EdgeRecord]:
        """获取从指定任务出发的边"""
        pass

    def create_workflow_from_blueprint(self, blueprint: PlanBlueprint) -> bool:
        """在一个业务级事务中，根据蓝图创建任务和边。"""
        pass

    # ... 其他方法 ...
```

## 6. 测试策略 (Testing Strategy)

*   **单元测试**: 使用 `unittest` 或 `pytest` 对 `repository` 层的每个方法进行测试，使用内存数据库 (如 SQLite) 或 Mock 数据库连接。
*   **集成测试**: 在开发环境中，对 `service` 层的关键流程进行测试，连接真实的 PostgreSQL 实例。

## 7. 部署与依赖 (Deployment & Dependencies)

*   本服务作为 Python 包，通过 `pip` 安装依赖。
*   核心依赖: `psycopg2-binary`, `interfaces` 模块。
*   需要配置可访问的 PostgreSQL 数据库实例。

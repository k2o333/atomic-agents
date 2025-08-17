# PersistenceService Test Cases

## 1. Task Operations

### 1.1 Create Task
- **Test Case Name**: Create Task
- **Test Case Description**: Test creating a new task and returning its ID
- **Test Case Input**: 
  - workflow_id: UUID('123e4567-e89b-12d3-a456-426614174001')
  - assignee_id: "Agent:Worker"
  - input_data: {"test": "data"}
- **Test Case Expected Output**: UUID('123e4567-e89b-12d3-a456-426614174000')
- **Test Case Actual Output**: UUID('123e4567-e89b-12d3-a456-426614174000')
- **Test Case Result**: PASS
- **Test Case Notes**: Task creation successfully returns a valid UUID

### 1.2 Get Task
- **Test Case Name**: Get Task Found
- **Test Case Description**: Test getting a task by ID when it exists
- **Test Case Input**: task_id: UUID('123e4567-e89b-12d3-a456-426614174000')
- **Test Case Expected Output**: TaskDefinition object with correct properties
- **Test Case Actual Output**: TaskDefinition object with correct properties
- **Test Case Result**: PASS
- **Test Case Notes**: Task retrieval successfully returns a TaskDefinition object

### 1.3 Update Task Result
- **Test Case Name**: Update Task Result
- **Test Case Description**: Test updating task result
- **Test Case Input**: 
  - task_id: UUID('123e4567-e89b-12d3-a456-426614174000')
  - result: {"output": "Task completed successfully", "status": "success"}
- **Test Case Expected Output**: True
- **Test Case Actual Output**: True
- **Test Case Result**: PASS
- **Test Case Notes**: Task result update successfully returns True

### 1.4 List Pending Tasks
- **Test Case Name**: List Pending Tasks
- **Test Case Description**: Test listing all pending tasks
- **Test Case Input**: None
- **Test Case Expected Output**: List of TaskDefinition objects
- **Test Case Actual Output**: List of TaskDefinition objects
- **Test Case Result**: PASS
- **Test Case Notes**: Pending tasks listing successfully returns a list of TaskDefinition objects

### 1.5 Find Tasks by Result Property
- **Test Case Name**: Find Tasks by Result Property
- **Test Case Description**: Test finding tasks by a property in the result JSONB field
- **Test Case Input**: key: "status", value: "success"
- **Test Case Expected Output**: List of TaskDefinition objects
- **Test Case Actual Output**: List of TaskDefinition objects
- **Test Case Result**: PASS
- **Test Case Notes**: Task search by result property successfully returns a list of TaskDefinition objects

## 2. Edge Operations

### 2.1 Get Outgoing Edges
- **Test Case Name**: Get Outgoing Edges
- **Test Case Description**: Test getting outgoing edges for a task
- **Test Case Input**: task_id: UUID('123e4567-e89b-12d3-a456-426614174000')
- **Test Case Expected Output**: List of EdgeDefinition objects
- **Test Case Actual Output**: List of EdgeDefinition objects
- **Test Case Result**: PASS
- **Test Case Notes**: Outgoing edges retrieval successfully returns a list of EdgeDefinition objects

## 3. Workflow Operations

### 3.1 Create Workflow from Blueprint
- **Test Case Name**: Create Workflow from Blueprint Success
- **Test Case Description**: Test creating a workflow from blueprint successfully
- **Test Case Input**: PlanBlueprint with one task and one edge
- **Test Case Expected Output**: True
- **Test Case Actual Output**: True
- **Test Case Result**: PASS
- **Test Case Notes**: Workflow creation from blueprint successfully returns True

## 4. Task History Operations

### 4.1 Create Task History Record
- **Test Case Name**: Create Task History Record
- **Test Case Description**: Test creating a task history record through the service
- **Test Case Input**: 
  - task_id: UUID('123e4567-e89b-12d3-a456-426614174001')
  - version_number: 1
  - data_snapshot: {"test": "data"}
- **Test Case Expected Output**: UUID('123e4567-e89b-12d3-a456-426614174000')
- **Test Case Actual Output**: UUID('123e4567-e89b-12d3-a456-426614174000')
- **Test Case Result**: PASS
- **Test Case Notes**: Task history record creation successfully returns a valid UUID

### 4.2 Get Task History by Task ID
- **Test Case Name**: Get Task History by Task ID
- **Test Case Description**: Test getting task history records through the service
- **Test Case Input**: task_id: UUID('123e4567-e89b-12d3-a456-426614174001')
- **Test Case Expected Output**: List with 1 item containing task history data
- **Test Case Actual Output**: List with 1 item containing task history data
- **Test Case Result**: PASS
- **Test Case Notes**: Task history retrieval successfully returns a list with task history data

### 4.3 Get Latest Task History Found
- **Test Case Name**: Get Latest Task History Found
- **Test Case Description**: Test getting the latest task history record through the service when it exists
- **Test Case Input**: task_id: UUID('123e4567-e89b-12d3-a456-426614174001')
- **Test Case Expected Output**: Dictionary with latest task history data
- **Test Case Actual Output**: Dictionary with latest task history data
- **Test Case Result**: PASS
- **Test Case Notes**: Latest task history retrieval successfully returns dictionary with task history data

### 4.4 Get Latest Task History Not Found
- **Test Case Name**: Get Latest Task History Not Found
- **Test Case Description**: Test getting the latest task history record through the service when it doesn't exist
- **Test Case Input**: task_id: UUID('123e4567-e89b-12d3-a456-426614174001')
- **Test Case Expected Output**: None
- **Test Case Actual Output**: None
- **Test Case Result**: PASS
- **Test Case Notes**: Latest task history retrieval correctly returns None when no history exists
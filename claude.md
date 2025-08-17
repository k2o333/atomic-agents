# 大规则
只允许修改项目代码目录下的文件！！
只允许读取项目代码目录下的文件，项目的python虚拟环境，其他文件补充内的目录和文件！！
每次日志中有error必然要查询deepwiki mcp，但要知道可能要查哪个开源仓库


# 项目信息

## 项目代码目录
/root/projects/atom_agents

## 项目使用框架


## 项目日志目录在(我不让你读别读！！！)


## 项目的python虚拟环境：
/root/projects/atom_agents/myenv311

## 项目主程序：


## 文档：
/root/projects/atom_agents/静态能力和蓝图json.md
/root/projects/atom_agents/系统模块说明.md
/root/projects/atom_agents/建议开发顺序.md
interfaces模块文档  /root/projects/atom_agents/interfaces/interfaces.md  还有同目录下readme
数据库和文件版本模块文档  /root/projects/atom_agents/PersistenceService/PersistenceService.md  还有同目录下readme
agentservice模块文档   /root/projects/atom_agents/agentservice/AgentService.md  还有同目录下readme
中央图引擎模块文档  /root/projects/atom_agents/CentralGraphEngine/CentralGraphEngine.md  还有同目录下readme
日志服务模块文档   /root/projects/atom_agents/LoggingService/LoggingService.md   还有同目录下readme
LLMService模块文档  /root/projects/atom_agents/LLMService/LLMService.md   还有同目录下readme
agents模块文档   /root/projects/atom_agents/agents/agents.md    还有同目录下readme
toolservices文档    /root/projects/atom_agents/toolservices/toolservices.md  还有同目录下readme



## 需要的配置信息
/root/projects/atom_agents/.env  尤其数据库配置信息都在这里


## mcp使用要求
任何不熟悉的文档调用context7 mcp
修改文件不能用serena mcp！！


# 开发习惯

## 模块要求
### 每个模块只有一个入口文件

### 测试文档：
每次开发完一个模块，（还没测试的时候）要写一个test.md
每次修改一个模块，都要根据修改内容，在test.md中增加或者修改测试用例

test.md需要包含所有需要的测试用例，每个测试用例要包含的信息有：
1，测试用例名称
2，测试用例描述
3，测试用例输入
4，测试用例预期输出
5，测试用例实际输出
6，测试用例结果
7，测试用例备注

### 测试脚本撰写和测试
#### 每个模块测试脚本都要放在该模块test目录下，测试脚本的名称要和模块的名称相同，只是后缀名改为_test.py
#### 根据test.md写测试脚本
#### 测试达到test.md的预期，才算测试完成


### 写readme
每次测试完一个模块（不论新开发还是修改），都需要写一个readme.md 其中要包括

* 简介：模块名称、一句话描述、主要功能概述
* 安装/部署：依赖项、环境要求、安装步骤、配置说明
* 快速开始：最简单的使用示例，让用户快速跑起来
* API/接口文档：详细的接口说明（方法、参数、返回值、错误码）、使用示例
* 配置：配置项说明、配置文件示例、环境变量
* 使用指南：常见场景的详细使用步骤、最佳实践
* 架构/设计：高层架构图、核心组件说明（帮助理解维护）
* 开发指南：如何构建、运行测试、贡献代码
* 故障排查：常见问题、错误信息及解决方案、日志位置
* 变更日志：版本更新记录
* “如何用/维护”：提供操作指南、接口说明、配置方法、排错信息。是手册。



## 任何文件多于500行代码，一定要拆分。
在没有特别说明的情况下，拆分方式为：比如，一个代码文件叫report.py，那么拆分为report_service.py、report_controller.py、report_model.py（名称仅为举例）。拆分后不需要保证不需要修改拆分代码以外的代码文件。由原文件report.py处理其他代码文件的调用，其他文件只能和report.py互相调用。几个拆分后的文件代码量最好大致相当

## 每次开发完都要写测试脚本，测试重点功能和整体流程。验收没有问题了任务才结束
# COMP3019J 项目

[English](README.md) | 简体中文

### 项目名称：BJUT 统一身份认证系统

### 团队_20 成员：

* 张博涵 22207251
* 高云涵 22207250
* 刘乐 22207256

### 项目描述

本项目旨在设计和实现一个综合性的大学网站，为不同类型的用户提供个性化和功能性的体验。该网站为学生、教师、图书馆工作人员和其他安保人员提供了一个界面，用于管理他们的个人资料、与他人互动，并根据其角色访问大学资源。

### 核心功能
1. 统一身份认证
2. 课程管理系统
3. 图书馆管理系统
4. 电动车注册系统
5. 论坛平台
6. 主题定制
7. 系统日志

### 项目预览

这是项目的**预览版本**。请使用Python在本地运行此项目以查看最新网站。

[http://webappdev.zhangbh.com/](http://webappdev.zhangbh.com/)

### 运行项目

#### 环境配置

1. 安装 Python 3.10
2. 使用以下代码配置环境：

```shell
python -V                 # 输出Python版本用于调试
pip install virtualenv
virtualenv venv
source venv/bin/activate  # Linux/Mac系统
venv\Scripts\activate     # Windows系统
pip install -r requirements.txt
```

#### 运行Web服务器

```shell
flask run
```

或

```shell
python run.py
```

#### 访问网站

网址：http://localhost:5000 或 http://127.0.0.1:5000

### 特色功能

* 基于角色的访问控制
* CSRF 保护
* 蓝图架构
* 密码加密
* 完整的日志系统
* 主题定制（明暗模式）
* ![image](Project%20Document/STYLE.gif)
* JavaScript表单验证
* ![image](Project%20Document/JS.gif)
* AJAX动态更新
* ![image](Project%20Document/AJAX_S.gif)
* ![image](Project%20Document/AJAX_T.gif)

### 系统角色

1. 系统管理员
   - 用户管理：添加、编辑和删除用户账户
   - 系统配置：管理网站设置
   - 日志监控和系统维护
   - 访问所有系统功能

2. 学生
   - 课程管理：查看和注册课程
   - 成绩查看：查看个人学业成绩
   - 图书馆访问：搜索图书和查看借阅历史
   - 电动车注册：注册个人电动车
   - 论坛参与：参与讨论
   - 个人资料管理：更新个人信息
   - 主题定制：修改界面外观

3. 教师
   - 课程管理：创建和管理课程
   - 学生管理：处理课程注册
   - 成绩管理：输入和更新成绩
   - 图书馆访问：搜索和借阅资源
   - 论坛参与：创建和管理讨论
   - 个人资料管理：更新个人信息
   - 主题定制：修改界面外观

4. 图书馆工作人员
   - 资源管理：管理图书馆库存
   - 借阅记录管理：处理借阅记录
   - 个人资料管理：更新个人信息
   - 主题定制：修改界面外观

5. 安保人员
   - 电动车注册审批：审核学生申请
   - 个人资料管理：更新个人信息
   - 主题定制：修改界面外观

6. 访客
   - 图书馆目录浏览：搜索可用资源
   - 联系信息访问：查看部门详情

### 技术细节

* 后端框架：Python Flask
* 数据库：MySQL 配合 SQLAlchemy ORM
* 前端：
  - HTML5 & CSS3
  - JavaScript 实现动态交互
* 认证：Flask-Login
* 表单处理：Flask-WTF
* 安全特性：
  - CSRF 保护
  - 密码哈希
  - 会话管理
  - 基于角色的访问控制

### 项目结构

```shell
app/
├── api/
├── static/        # 静态资源（CSS、JS、图片）
├── templates/     # HTML模板
├── utils/         # 工具函数
├── routes.py/     # 路由控制器
├── models.py/     # 数据库模型
└── forms.py/      # 表单类
```

### 测试账号

角色 | 用户名 | 密码
---|---|---
管理员 | le.liu@emails.bjut.edu.cn | 123
学生 | bohan.zhang@ucdconnect.ie | 20040422
教师 | 2742707462@qq.com | 20040422
图书馆工作人员 | gaoyunhan0@gmail.com | 123456
安保人员 | mty@gmail.com | 20040422

### 未来开发计划

1. 增强用户体验
   - 改进UI/UX设计
   - 移动端响应优化
   - 实时通知功能

2. 高级功能
   - 高级基于角色的访问控制
   - API集成能力
   - 移动应用开发
   - 性能优化
   - 增强安全措施

3. 系统扩展
   - 增加用户角色
   - 更多定制选项
   - 与其他大学系统集成

### 文件和目录结构

```shell
web-application/
├── app/                 # 详见项目结构
├── logs/                # 管理员用网站日志
├── Project Document/    # 项目文档和视频
├── tests/               # 测试
├── .env/                # 环境变量
├── .env.example/        # 环境变量示例
├── .gitignore/ 
├── config.py/           # 配置文件
├── README.md/
├── requirements.txt/
└── run.py/
```

### 联系方式

如有任何问题或建议，请联系：
邮箱：beihaizhang11@gmail.com
地址：北京市朝阳区平乐园100号

### 代码仓库

仓库地址：https://csgitlab.ucd.ie/webApplication/web-application

### 许可证

MIT 许可证

版权所有 (c) 2024 团队20 张博涵、高云涵和刘乐

特此免费授予任何获得本软件和相关文档文件（"软件"）副本的人不受限制地处理本软件的权利，包括但不限于使用、复制、修改、合并、发布、分发、再许可和/或出售本软件副本的权利，并允许向其提供本软件的人这样做，但须符合以下条件：

上述版权声明和本许可声明应包含在本软件的所有副本或重要部分中。

本软件按"原样"提供，不提供任何形式的明示或暗示的保证，包括但不限于对适销性、特定用途的适用性和非侵权性的保证。在任何情况下，作者或版权持有人均不对任何索赔、损害或其他责任负责，无论是在合同诉讼、侵权行为还是其他方面，产生于本软件或与本软件的使用或其他交易有关。 
# kingbaseslot-exporter

## 项目介绍

`kingbaseslot-exporter` 是一个用于监控 KingbaseES 数据库复制槽状态的 Prometheus exporter。
它定期查询 KingbaseES 数据库的复制槽信息，并将这些信息转换为 Prometheus 可识别的指标格式，以便进行监控和告警。

## 支持的数据库
KingbaseES V8R6
KingbaseES V9

## 技术栈

- **语言**: Python 3.9+
- **框架**: FastAPI
- **依赖管理**: pip (详见 `requirements.txt`)

## 安装与部署

### 前提条件

- 已安装 Python 3.9+ 环境。
- 已有 KingbaseES 数据库，并配置了相应的用户权限以查询复制槽信息。
- 推荐使用虚拟环境 (例如 venv 或 conda)。

### 本地运行

1.  克隆项目到本地 (如果尚未克隆)：
    ```bash
    git clone <项目仓库地址> # 如果您已在项目目录中，可跳过此步
    cd kingbaseslot-exporter
    ```
2.  创建并激活虚拟环境 (可选但推荐)：
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    # source venv/bin/activate
    ```
3.  安装依赖：
    ```bash
    pip install -r requirements.txt
    ```

### 配置

`kingbaseslot-exporter` 通过环境变量进行配置。主要环境变量包括：

-   `DB_HOST`: KingbaseES 数据库主机名或IP地址。
-   `DB_PORT`: KingbaseES 数据库端口 (默认为 `54321`)。
-   `DB_USER`: 连接数据库的用户名 (默认为 `system`)。
-   `DB_PASSWORD`: 连接数据库的密码 (默认为空字符串, 请务必设置)。
-   `DB_NAME`: 要连接的数据库名称 (默认为 `test`)。

请根据您的实际环境设置这些环境变量。例如，在 Linux/macOS上:
```bash
export DB_HOST=your_kingbase_host
export DB_PORT=54321
export DB_USER=system
export DB_PASSWORD=your_secret_password
export DB_NAME=test
```
在 Windows PowerShell 中:
```powershell
$env:DB_HOST = "your_kingbase_host"
$env:DB_PORT = "54321"
$env:DB_USER = "system"
$env:DB_PASSWORD = "your_secret_password"
$env:DB_NAME = "test"
```

### 运行

设置完环境变量后，使用 uvicorn 运行 FastAPI 应用 (确保您在项目的根目录下，即 `kingbaseslot-exporter.py` 所在的目录)：

```bash
uvicorn kingbaseslot-exporter:app --host 0.0.0.0 --port 8001
```

### Docker部署

项目提供了 `Dockerfile` 和 `deploy/docker-compose.yml` 用于 Docker部署。

1.  **使用 Dockerfile 构建和运行**:
    在项目根目录下执行：
    ```bash
    # 构建镜像
    docker build -t kingbaseslot-exporter:latest .
    # 运行容器 (请替换环境变量为您的实际值)
    docker run -d -p 8001:8001 \
      -e DB_HOST=your_db_host \
      -e DB_PORT=54321 \
      -e DB_USER=your_db_user \
      -e DB_PASSWORD=your_db_password \
      -e DB_NAME=your_db_name \
      --name kingbaseslot-exporter-container \
      kingbaseslot-exporter:latest
    ```

2.  **使用 docker-compose 运行 (推荐用于本地开发和测试)**:
    编辑 `deploy/docker-compose.yml` 文件，根据需要修改环境变量，然后在 `deploy` 目录下运行：
    ```bash
    cd deploy
    docker-compose up -d
    ```

### Kubernetes部署

项目提供了 `deploy/kingbaseslot-exporter-deployment-service.yaml` 用于 Kubernetes 部署。

1.  根据您的 Kubernetes 集群和 KingbaseES 数据库信息修改 `deploy/kingbaseslot-exporter-deployment-service.yaml` 文件中的环境变量和镜像地址 (例如 `image: moqihzh/kingbaseslot-exporter:v0.1`)。
2.  应用部署和服务：
    ```bash
    kubectl apply -f deploy/kingbaseslot-exporter-deployment-service.yaml
    ```

## 使用

启动 exporter 后，可以通过以下端点访问：

-   健康检查: `http://<exporter-host>:8001/health`
-   Prometheus 指标: `http://<exporter-host>:8001/metrics`

在 Prometheus 的配置文件 (`prometheus.yml`) 中添加以下抓取配置：

```yaml
scrape_configs:
  - job_name: 'kingbaseslot_exporter'
    metrics_path: /metrics
    schema: http
    static_configs:
      - targets: ['<kingbaseslot-exporter-service-or-ip>:8001'] # 例如: 在Kubernetes中可能是 'kingbaseslot-exporter.monitoring.svc.cluster.local:8001' 或本地运行时的 'localhost:8001'
```

# 电商自动化测试项目理解图谱

这份文档帮助你从“业务流程、代码结构、token 鉴权、测试执行链路、实习学习重点”五个角度理解当前项目。

## 1. 项目整体结构

```mermaid
flowchart LR
    Tester["测试人员 / 实习生"] --> Pytest["pytest 测试运行器"]

    Pytest --> Fixtures["conftest.py<br/>测试配置和夹具"]
    Pytest --> ApiTests["test_api_flow.py<br/>API 自动化用例"]
    Pytest --> UiTests["test_ui_flow.py<br/>可选 UI 冒烟用例"]

    Fixtures --> Client["api_client.py<br/>ShopApiClient"]
    ApiTests --> Client

    Client --> DummyJSON["DummyJSON 电商测试 API"]
    UiTests --> SauceDemo["Sauce Demo 网页"]

    DummyJSON --> Auth["登录 / 刷新 token"]
    DummyJSON --> User["用户信息"]
    DummyJSON --> Cart["购物车"]
```

你可以把这个项目理解成一个小型自动化测试框架：

- `pytest` 负责发现和执行测试。
- `conftest.py` 负责准备公共测试对象，比如已经登录好的 API client。
- `api_client.py` 负责封装接口请求，不让测试用例直接写一堆重复的 `requests.post/get`。
- `test_api_flow.py` 写真实业务断言，比如“能登录”“能刷新 token”“能加购物车”。
- `test_ui_flow.py` 是可选 UI 测试，只有加 `--run-ui` 才运行。

## 2. 真实 token 获取流程

```mermaid
sequenceDiagram
    participant Test as pytest 用例
    participant Fixture as conftest.py fixture
    participant Client as ShopApiClient
    participant API as DummyJSON API

    Test->>Fixture: 请求 api_client
    Fixture->>Client: 创建 ShopApiClient(base_url)
    Fixture->>Client: login(username, password)
    Client->>API: POST /auth/login
    API-->>Client: accessToken + refreshToken + 用户信息
    Client->>Client: 保存 AuthTokens
    Fixture-->>Test: 返回已登录 client
    Test->>Client: get_user_profile()
    Client->>API: GET /auth/me<br/>Authorization: Bearer accessToken
    API-->>Client: 当前用户资料
    Client-->>Test: JSON 数据
```

这就是你之前“拿不到真实 token”的核心位置。旧代码取的是 `token` 字段，但现在 DummyJSON 返回的是 `accessToken`。当前项目已经兼容：

- 优先取 `accessToken`
- 兼容旧 mock 里的 `token`
- 保存 `refreshToken`
- 后续请求自动带 `Authorization: Bearer <accessToken>`

## 3. 电商业务测试链路

```mermaid
flowchart TD
    Start["开始测试"] --> Login["登录用户<br/>POST /auth/login"]
    Login --> TokenOk{"拿到<br/>accessToken?"}

    TokenOk -- 否 --> FailAuth["认证失败<br/>测试终止并报错"]
    TokenOk -- 是 --> Profile["获取用户资料<br/>GET /auth/me"]

    Profile --> ProfileAssert["断言 username / email 正确"]
    ProfileAssert --> Refresh["刷新会话<br/>POST /auth/refresh"]
    Refresh --> RefreshAssert["断言新 token 可继续使用"]

    RefreshAssert --> AddCart["添加商品到购物车<br/>POST /carts/add"]
    AddCart --> CartAssert["断言 userId / 商品 id / 数量"]

    CartAssert --> GetCart["查询用户购物车<br/>GET /carts/user/1"]
    GetCart --> Done["API E2E 流程通过"]
```

这里的“E2E”不是只看页面，而是从用户身份开始，走到核心业务动作：

1. 用户能登录。
2. token 能被真实接口接受。
3. token 能刷新。
4. 用户能完成购物车业务。
5. 返回数据符合预期。

这就是接口自动化里非常常见的一条主链路。

## 4. 代码职责分层

```mermaid
flowchart TB
    subgraph Tests["测试层：写业务断言"]
        T1["test_login_returns_real_access_token"]
        T2["test_refresh_auth_session"]
        T3["test_add_product_to_cart"]
        T4["test_get_user_cart_items"]
    end

    subgraph Fixtures["夹具层：准备测试上下文"]
        F1["base_url"]
        F2["api_credentials"]
        F3["api_client<br/>自动登录"]
    end

    subgraph Client["客户端层：封装 HTTP 细节"]
        C1["login"]
        C2["refresh_auth_session"]
        C3["get_user_profile"]
        C4["add_to_cart"]
        C5["get_cart_items"]
        C6["_request<br/>统一 headers / timeout / retry"]
    end

    subgraph External["外部系统"]
        E1["DummyJSON API"]
        E2["Sauce Demo UI"]
    end

    Tests --> Fixtures
    Fixtures --> Client
    Client --> External
```

实习里你会经常听到“分层设计”。这个项目现在就是一个简化版：

- 测试层只关心“业务对不对”。
- 夹具层负责“测试前要准备什么”。
- 客户端层负责“怎么请求接口”。
- 外部系统是真实被测服务。

好的自动化测试项目，通常不会把所有东西都塞进一个测试函数里。

## 5. pytest 执行流程

```mermaid
flowchart LR
    Cmd["python -m pytest -q"] --> Collect["收集 test_*.py"]
    Collect --> LoadConfig["读取 pytest.ini"]
    LoadConfig --> LoadFixtures["加载 conftest.py"]
    LoadFixtures --> RunApi["运行 API 用例"]
    LoadFixtures --> UiDecision{"是否传入<br/>--run-ui?"}

    UiDecision -- 否 --> SkipUi["跳过 UI 用例"]
    UiDecision -- 是 --> RunUi["启动 Edge WebDriver<br/>运行 UI 冒烟测试"]

    RunApi --> Report["输出测试报告"]
    SkipUi --> Report
    RunUi --> Report
```

当前默认命令：

```powershell
python -m pytest -q
```

默认只跑 API 自动化。UI 测试需要浏览器和 WebDriver，所以用下面命令显式开启：

```powershell
python -m pytest -q --run-ui
```

## 6. 自动化测试实习学习地图

```mermaid
mindmap
  root((自动化测试实习))
    API 测试
      HTTP 方法
      状态码
      JSON 断言
      token 鉴权
      请求重试
    pytest
      测试发现
      fixture
      参数化
      skip 和 marker
      测试报告
    业务理解
      登录
      用户资料
      商品
      购物车
      订单
    UI 自动化
      Selenium
      元素定位
      等待机制
      浏览器驱动
      冒烟测试
    工程能力
      目录结构
      依赖管理
      环境变量
      日志和错误信息
      CI/CD
```

如果你以后继续完善这个项目，可以按这个顺序进阶：

1. 先把 API 主链路稳定跑通。
2. 再补更多业务接口，比如商品查询、订单创建、异常登录。
3. 再加参数化，把多个用户、多个商品组合跑起来。
4. 再加测试报告，比如 `pytest-html` 或 Allure。
5. 最后再把 UI 自动化接进来，做少量关键冒烟测试。

## 7. 一句话理解这个项目

这个项目的核心价值是：用 pytest 驱动真实接口请求，通过 `ShopApiClient` 获取并携带真实 `accessToken`，验证一个电商用户从登录到购物车操作的关键业务链路是否可用。

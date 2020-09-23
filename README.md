
-   目录

    -   [概述](#概述)
    -   [事件定义](#事件定义)
    -   [开发规范](#开发规范)
    -   [数据库结构](#数据库结构)
    -   [接口说明](#接口说明)
    -   [常见问题]()

## 概述

### 技术要点详述

####   token的声明周期

1.  用户未登录

    -   前端肯定 没有 token

2.   用户执行注册登录

    1.   一旦基础数据校验成功,后端生成 token, 并且 token 包含此次注册 / 登录用户的用户名，通过 response 返回给前端 [json]
    2.  前端拿到 token 后,存入浏览器本地存储 window.localStorage.setItem('dnblog, token)

3.  用户每次访问博客页面 [ flask 前端5000端口 ]
    
    1.  从本地存储中拿出 token -> window.localStorage.getItem('dnblog')
    2.  JS 将 token 放入 request 的 Authorization 头,发送http请求向后端索要数据
    3.  服务器 - 接到前端请求 [ 当前URL 加了 login_check 并且请求方法在 methods参数 中]
        -   eg. login_check('POST'),则 当前URL POST 方法时 进行如下校验
        1.  从 request 的 Authorization 头中，拿到 token
        2.  校验
        3.  校验不通过,返回前端异常码
        4.  校验通过,正常热行对应URL的视图函数

4.  前端一旦接到关于 token 的异常码,则删除本地存储中的 token 且将用户转至登录界面

## 事件定义

1.  注册
2.  登录
3.  修改个人信息

## 开发规范

1.  后端环境

    -   python  3.8.2 + django 1.11.8 + mysql 8.0.21 + Ubuntu 18.04 + vim

2.  通信协议

    -   http

3.  通信格式

    -   json

4.  API 规范

    -   一定程度上 符合 RESTful 规范

## 数据库结构

### user 表

|  字段名  |      类型       |   作用   |           备注1            | 备注2 |
| :------: | :-------------: | :------: | :------------------------: | :---: |
| username |   varchar(11)   |  用户名  | 注册时填写用户名，不可修改 | 主键  |
| nickname |   varchar(30)   |   昵称   | 在博客中显示的名字，可修改 |  无   |
|  email   |   varchar(50)   |   邮箱   |            预留            |  无   |
| password |   varchar(40)   |   密码   |     用户密码已散列存储     |  无   |
|   sign   |   varchar(50)   | 个人签名 |             无             |  无   |
|   info   |  varchar(150)   | 个人描述 |             无             |  无   |
|  avatar  | ImageField(100) |   头像   |             无             |  无   |

### topic 表

|    字段名     |    类型     |   作用   |      备注1       |       备注2        |
| :-----------: | :---------: | :------: | :--------------: | :----------------: |
|      id       |     int     |   标题   |        无        |     自增 主键      |
|     title     | varchar(50) |   标题   |        无        |         无         |
|    author     | foreign key |   作者   |        无        | UserProfile 的外键 |
|   category    | varchar(20) |   分类   |   no-tec / tec   |         无         |
|     limit     | varchar(10) |   权限   | public / private |         无         |
|  create_time  |  datetime   | 创建时间 |        无        |         无         |
| modified_time |  datetime   | 更改时间 |        无        |         无         |
|    content    |    text     | 博客内容 |        无        |         无         |
|   introduce   | varchar(90) | 博客摘要 |        无        |         无         |


## 接口说明

### 用户登录注册接口

#### 注册接口

> URL：http://127.0.0.1:8000/v1/users

1.  请求方式

    -   POST

2.  请求格式

    -   json 具体参数如下

|   字段    |       含义       | 类型  | 备注  |
| :-------: | :--------------: | :---: | :---: |
| username  |      用户名      | char  | 必填  |
|   email   |     用户邮箱     | char  | 必填  |
| password1 | 第一次输入的密码 | char  | 必填  |
| password2 | 第二次输入的密码 | char  | 必填  |

-   请求示例：
    -   `{'username':'xxx','email':'xxx','password1':'xxx','password2':'xxx'}`

3.  响应格式

    -   json 具体参数如下

|   字段   |             含义             | 类型  |                      备注                       |
| :------: | :--------------------------: | :---: | :---------------------------------------------: |
|   code   |             状态             |  int  |  请求成功，code 为 200，请求失败 见 **异常码**  |
| username |            用户名            | char  |                       无                        |
|   data   | 返回具体的数据都包含在data中 |  {}   | {token:xxx 此为会话保持用的令牌 - char，。。。} |

-   响应示例：
    -   `{'code':200,'username':'xxx','data':{'token':'xxx'}}`

-   异常码

| 异常码 |         含义         |           备注           |
| :----: | :------------------: | :----------------------: |
|  202   |      请求无内容      |                          |
|  203   |   请求未提交用户名   |                          |
|  204   |    请求未提交邮箱    |                          |
|  205   |    请求未提交密码    |                          |
|  206   | 两次提交的密码不一致 | password_1 != password_2 |
|  207   |     用户名已存在     |                          |
|  500   |      服务器异常      |                          |

-   异常响应示例：`{'code':203,'error':'pl. transfer username' }` 

#### 获取用户数据接口

> URL：http://127.0.0.1:8000/v1/users/<username>

1.  请求方式

    -   GET
    
2.  请求格式

    1.  直接 GET 请求，可获取全量数据
    2.  GET 请求后添加查询字符串，可根据具体的查询字符串查询 `http://127.0.0.1:8000/v1/users/<username>?nickname=1`
    
3.  响应格式

    -   json 具体参数如下

|   字段   |      含义      | 类型  |                     备注                      |
| :------: | :------------: | :---: | :-------------------------------------------: |
|   code   |      状态      |  int  | 请求成功，code 为 200，请求失败 见 **异常码** |
| username |     用户名     | char  |           此次欲获取的用户的用户名            |
|   data   | 返回的具体数据 |  {}   |         {'info':'xx','sign':'xx',...}         |

-   响应示例：
    
    -   全量响应：
        -   `{'code':200,'username':'xx','data':{'nickname':'xxx','sign':'xxx','info':'xx'','avatar':'xxx'}}`
    -   局部响应：
        -   `{'code':200,'username':'xx','data':{'nickname':'xxx'}}`

-   异常码

| 异常码 |     含义     | 备注  |
| :----: | :----------: | :---: |
|  208   | 用户名不存在 |       |

-   异常响应示例：`{'code':208,'error':'pl. transfer username' }` 

#### 修改用户个人信息接口

> URL：http://127.0.0.1:8000/v1/users

1.  请求方式

    -   PUT    
    
2.  请求格式

    -   json 具体参数如下

|   字段   |   含义   | 类型  |  备注  |
| :------: | :------: | :---: | :----: |
| nickname |   昵称   | char  | 非必填 |
|   sign   | 个人签名 | char  | 非必填 |
|   info   | 个人描述 | char  | 非必填 |

-   该请求需要客户端在 HTTP header 里 添加 token：`Authorization: token`

-   请求示例：
    -   `{'nickname':'xxx','sign':'xxx','info':'xxx'}`
    
3.  响应格式

    -   json 具体参数如下

|   字段   |  含义  | 类型  |           备注            |
| :------: | :----: | :---: | :-----------------------: |
|   code   |  状态  |  int  | 默认正常：200，异常见 1.4 |
| username | 用户名 | char  |            无             |

-   响应示例：
    -   `{'code':200,'username':'xxx'}`
    
-   异常码

| 异常码 |      含义      | 备注  |
| :----: | :------------: | :---: |
|  202   |   请求无内容   |       |
|  208   |   用户不存在   |       |
|  209   | 请求未提交昵称 |       |

-   异常响应示例：`{'code':202,'error':'user not exist' }` 

### 博客内容接口

#### 发表博客

> URL：http://127.0.0.1:8000/v1/topics/<username>

1.  请求方式

    -   POST

2.  请求格式

    -   json 具体参数如下

|     字段     |         含义         | 类型  |                备注                 |
| :----------: | :------------------: | :---: | :---------------------------------: |
|    title     |         标题         | char  |                必填                 |
|   category   |         分类         | char  | tec: 技术类别<br>no-tec：非技术类别 |
|    limit     |         权限         | char  |    public：公开<br>private：私有    |
|   content    | 博客内容带 HTML 格式 | char  |                必填                 |
| content_text |    博客纯文本格式    | char  |                必填                 |

-   请求示例：
    -   `{'title':'haha','category':'xxx','limit':'xxx','content':'xxx','content_text':'xxx'}`
    -   该请求需要客户端 HTTP header 里添加 token, 格式如下：'Authorization:token'

3.  响应格式

    -   json 具体参数如下

|   字段   |  含义  | 类型  |                     备注                      |
| :------: | :----: | :---: | :-------------------------------------------: |
|   code   |  状态  |  int  | 请求成功，code 为 200，请求失败 见 **异常码** |
| username | 用户名 | char  |                      无                       |

-   响应示例：
    -   `{'code':200,'username':'xxx'}`


#### 获取用户博客列表接口

> URL：http://127.0.0.1:8000/v1/topics/<username>?category=[tec|no-tec]

1.  请求方式

    -   GET

2.  请求格式

    1.  http://127.0.0.1:8000/v1/topics/<username> 可获取用户全量数据
    
    2.  http://127.0.0.1:8000/v1/topics/<username>?category=[tec|no-tec] 可获取用户具体分类的数据

3.  响应格式

    -   json 具体参数如下

| 字段  |            含义            | 类型  |                                  备注                                   |
| :---: | :------------------------: | :---: | :---------------------------------------------------------------------: |
| code  |            状态            |  int  |              请求成功，code 为 200，请求失败 见 **异常码**              |
| data  | 返回的具体数据都在 data 中 |  {}   | nickname char 昵称 <br>topics 用户文章列表 [] 具体内容详见 **响应示例** |

-   响应示例：

    ```json
        {
        "code": 200,
        "data": {
            "nickname": "xxx",
            "topics": [
              {
                "id": 1,
                "title": "xxx",
                "category": "xxx",
                "create_time": "xxx",
                "content": "xxx",
                "introduce": "xxx",
                "author": "nickname"
              }
            ] 
        }
    }
    ```
   
   
#### 获取用户具体博客内容接口

> URL：http://127.0.0.1:8000/v1/topics/<username>?id=000

1.  请求方式

    -   GET
    
2.  请求格式

    -   http://127.0.0.1:8000/v1/topics/<username> 地址后加查询字符串：t_id, 值为具体博客文章的id

3.  响应示例

    ```json
        {
        "code": 200,
        "data": {
            "nickname": "xxx",
            "title":"xxx",
            "category": "tec",
            "create_time": "0000-00-00",
            "content": "xxx",
            "introduce": "xxx",
            "author": "xxx",
            "next_id": null,
            "next_title": null,
            "previous_id": 0,
            "previous_title": "xxx",
            "message": [
              {
                "id": 1,
                "content": "xxx",
                "publisher": "xxx",
                "publisher_avatar": "url",
                "reply": [{
                  "publisher": "xx",
                  "publisher_avatar": "url",
                  "create_time": "0000-00-00 00:00:00",
                  "content": "xx",
                  "msg_id": 0
                }],
                "create_time":"0000-00-00 00:00:00"
              }
            ],
            "messages_count": 0
        }
    }
    ```
 
#### 删除博客接口
    
> URL：http://127.0.0.1:8000/v1/topics/<username>?t_id=1111

1.  请求方式

    -   DELETE

2.  请求格式

    -   url 地址访问
    
3.  响应示例

    -   `{"code":200}`

### 用户评论接口

> 有留言功能和回复功能，即留言的信息可以被回复。

#### 发表评论

> URL：http://127.0.0.1:8000/v1/messages/<topic_id>

1.  请求方式

    -   POST

2.  请求格式

    -   json 具体参数如下

|   字段    |   含义    | 类型  |  备注  |
| :-------: | :-------: | :---: | :----: |
|  content  | 留言内容  | char  |  必填  |
| parent_id | 父留言 id |  int  | 非必填 |

3.  响应示例

    -   `{"code": 200, "data":{"content":"xxx"}}`
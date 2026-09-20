# README

## 项目名称
箭头迷宫，又名一箭又一箭

## 游戏简介
“一箭又一箭”是一类点击式箭头解谜游戏。
玩家需要观察箭头的方向和相互阻挡关系，按照合适的顺序点击箭头，使所有箭头依次飞出棋盘。
其规则容易理解，但在实现过程中需要处理二维坐标、方向判断、路径检测、碰撞反馈和关卡状态等问题。
本游戏参考微信小程序，一箭又一箭

## 开发环境
本游戏采用 Python 作为开发语言，使用 Pygame 游戏开发库实现图形化界面。开发工具选用 VS Code，在 Windows 操作系统下进行开发调试。
Pygame 库提供窗口创建、图形绘制、鼠标事件监听、动画渲染等功能，实现游戏棋盘渲染、鼠标点击交互、碰撞检测以及通关失败弹窗界面。

## 安装和运行方法



1. 先前往[python 官网](https://www.python.org/),将鼠标移到download，然后点击python 3.14.7进行下载，下载安装时勾选 **Add Python to PATH**（非常重要，不勾选 cmd 识别不到 python）

<img width="1144" height="464" alt="image" src="https://github.com/user-attachments/assets/e1c0e4cd-a270-4e44-8f79-dc4b0f6b9173" />

2. 直接在 GitHub 网页点绿色「Code」→ Download ZIP，解压到本地文件夹

3. 安装依赖库
打开终端 / CMD/PowerShell，进入项目文件夹，执行下面命令，通过清华镜像源下载pygame：
```bash
pip install pygame -i https://pypi.tuna.tsinghua.edu.cn/simple
```
4. 运行游戏
打开终端，进入项目文件夹，输入
```bash
python main.py
```


## 游戏操作说明
## 游戏截图

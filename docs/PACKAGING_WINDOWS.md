# Windows 打包与运行说明

## 1. 必须运行 `dist` 里的 exe，不要运行 `build` 里的

| 目录 | 说明 |
|------|------|
| **`dist\PyXplore_Desktop\`** | ✅ **成品**：请在这里双击 `PyXplore_Desktop.exe` |
| **`build\PyXplore_Desktop\`** | ❌ **临时中间文件**：不完整，会出现 `Failed to load Python DLL` |

打包成功后，请打开：

```
D:\Aprogress\PyWPEM\dist\PyXplore_Desktop\PyXplore_Desktop.exe
```

整个 `dist\PyXplore_Desktop\` 文件夹要一起保留（内含 `_internal` 等依赖），不能只拷贝一个 exe 到别处（除非使用单文件模式另行配置）。

源码在打包目录内为 `_internal\src\`（与开发时 `import src.WPEM` 一致），勿再使用旧的 `PyXplore` 文件夹名。

## 2. 打包 Python 版本（推荐 3.10.18）

`build.bat` **不再使用 PATH 里的默认 `python`**（若默认是 **3.14**，PyInstaller 日志会显示 `Python: 3.14.0`，与预期不符）。

- 脚本默认使用：`D:\StabilityMatrix-win-x64\Data\Assets\Python\cpython-3.10.18-windows-x86_64-none\python.exe`
- 若你的 3.10.18 安装在其他位置，运行前设置环境变量：
  ```bat
  set PYTHON310_EXE=C:\你的路径\python.exe
  build.bat
  ```

打包时 PyInstaller 日志中应出现 **`Python: 3.10.x`**（及该解释器所在目录），而不是 `3.14`。

若使用 **Python 3.14** 等过新版本，PyInstaller 与部分轮子可能尚未完全适配，容易出现 `LoadLibrary`（加载 `python3xx.dll`）等问题。

## 3. 若仍报 DLL 错误：安装 VC++ 运行库

从微软官网安装 **Microsoft Visual C++ Redistributable**（x64）：

- 搜索：`Visual C++ Redistributable latest supported downloads`

安装后重启，再运行 `dist` 下的 exe。

## 4. 分发给其他用户

将整个文件夹 **`PyXplore_Desktop`**（`dist` 下那一整个目录）打成 zip 发给对方解压后运行其中的 exe 即可。

## 5. TensorFlow 与核心库 `src.WPEM`

- 计算核心即源码包 **`src.WPEM`**（不是名为 PyXplore 的独立 pip 库）。
- **CIF 预处理**等在默认参数下**不要求** TensorFlow；原先在 `Extinction/XRDpre.py` 顶层导入 `Relaxer` 会在**启动时**强行依赖 `tensorflow`。
- 已改为：仅在 **启用晶格弛豫（relaxation）** 时再加载 M3GNet/TensorFlow。  
  因此打包版可在**未打入 TensorFlow** 的情况下完成大部分功能；若需弛豫相关功能，请在打包环境中安装 TensorFlow 并保留 spec 中的相关 `hiddenimports`，或使用带 TensorFlow 的 Python 环境以开发模式运行。

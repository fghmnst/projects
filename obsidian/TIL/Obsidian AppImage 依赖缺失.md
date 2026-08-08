# 坑：Obsidian AppImage 依赖缺失

**日期**：2026-08-04
**场景**：WSL2 Ubuntu-24.04 安装 Obsidian Linux AppImage。

## 现象

- 启动报 `error while loading shared libraries: libnspr4.so: cannot open shared object file`
- 修完后再报 `libasound.so.2: cannot open shared object file`

## 原因

Electron 运行时依赖系统库。最小化 WSL 未装齐。`ldd <AppImage 解压后的 obsidian 可执行文件> | grep "not found"` 可一次列出全部缺失。

## 解决

```bash
sudo apt install -y libnspr4 libnss3 libasound2t64
```

- Ubuntu 24.04 音频库包名是 `libasound2t64`（旧版叫 `libasound2`，带 t64 后缀的是新命名）。
- 若缺库：把 AppImage 解压后 `ldd squashfs-root/obsidian | grep "not found"` 再装对应包。

## 关联

- AppImage 在无 libfuse2 的系统（如 24.04）需 `APPIMAGE_EXTRACT_AND_RUN=1` 运行。
- 官方 CLI 在 `~/.local/bin/obsidian`，要求 App 正在运行。

相关：[[30天学习 Index]] · [[术语表/术语表|术语表]]

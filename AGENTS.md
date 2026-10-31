# 映屿分发仓库

本仓库仅存放公开分发清单、说明与发布脚本，不提交 Flutter 源码、APK 或签名私钥。

# APK 下载分发规则

- 用户已确认 `https://gh-proxy.com/`（备用下载 2）在自己的网络可用。以后 Android 手机和 TV 的 APK 下载地址统一采用 `https://gh-proxy.com/https://github.com/arvin-manager/yingyu/releases/download/<tag>/<apk文件名>`。
- GitHub API 仍用于检查版本；Release 页面和附件原始元数据保留 GitHub 官方地址，勿将版本清单地址当成 APK 下载地址。
- 发布脚本先校验原始 GitHub 附件的包名、签名、架构、大小和 SHA-256，再在 `updates.json` 的 `downloadUrl` 加代理前缀。不得重复添加前缀，不更改 APK 字节、构建号、摘要或大小。
- 修改同一 APK 的下载代理不需要重新打包；禁止用同一构建号替换不同 APK。未经用户要求不打包或发布新 APK。

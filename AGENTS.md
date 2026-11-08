# 映屿分发仓库

本仓库仅存放公开分发清单、说明与发布脚本，不提交 Flutter 源码、APK 或签名私钥。

# APK 下载分发规则

- 用户已确认 `https://gh-proxy.com/`（备用下载 2）在自己的网络可用。以后 Android 手机和 TV 的 APK 下载地址统一采用 `https://gh-proxy.com/https://github.com/arvin-manager/yingyu/releases/download/<tag>/<apk文件名>`。
- GitHub API 仍用于检查版本；Release 页面和附件原始元数据保留 GitHub 官方地址，勿将版本清单地址当成 APK 下载地址。
- 发布脚本先校验原始 GitHub 附件的包名、签名、架构、大小和 SHA-256，再在 `updates.json` 的 `downloadUrl` 加代理前缀。不得重复添加前缀，不更改 APK 字节、构建号、摘要或大小。
- 修改同一 APK 的下载代理不需要重新打包；禁止用同一构建号替换不同 APK。未经用户要求不打包或发布新 APK。

# 蒲公英公开页面下载过渡

- 后续用户决定：版本检查继续 GitHub，APK 上传蒲公英；新版在内部解析公开页面下载，无账号 API Key、Cloudflare、登录或 Cookie。
- `pgyerChannels` 保存支持页面解析的新客户端清单；旧 `channels` 保留原可用版本，不把 HTML 页面链接下发给不会解析的旧客户端。首次过渡包需手动安装，不能宣称旧二进制自动获得新解析器。
- 发布前必须从蒲公英公开页面用生产 Dart 解析器重新下载 APK，SHA-256 与本地签名包一致后，使用 scripts/publish_pgyer.py 发布固定 build 页面，不固化 OSS 临时签名地址。
- scripts/update_feed.py 仍用于旧 GitHub 附件，沿用原 gh-proxy 规则；不要混淆两种分发方式。

# 三平台更新通道（2026-11-08）

- 手机 Android、TV、iOS 分别发布到 `pgyerChannels.android-mobile`、`android-tv`、`ios-mobile`，不能因 Android 手机与 iOS 共用 Bundle ID 字符串而复用条目。
- Android 使用公开页面解析与 App 内进度/安装器；iOS 打开平台独立的固定安装页，Ad Hoc 包仅支持描述文件内已登记设备。
- iOS 发布前核对 IPA 实际签名、个人团队、Bundle ID、构建号及设备配置，清单只包含公开版本元数据，不上传 UDID 名单。

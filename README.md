# 映屿 · 更新与安装包

版本检查使用公开 GitHub 清单；Android 手机、Android TV 和 iOS 分别从自己的蒲公英应用安装更新，无需自建服务器或蒲公英 API Key。

## 当前版本：1.1.25（5027）

| 平台 | 安装页 | 固定版本页 |
| --- | --- | --- |
| Android 手机 | [映屿 Android](https://www.pgyer.com/kankan-android-p) | [1.1.25](https://www.pgyer.com/app/build/857257175f161be202e9e76929f3756d) |
| Android TV | [映屿 TV](https://www.pgyer.com/yingyutv) | [1.1.25](https://www.pgyer.com/app/build/f5315921ad049b129a657a2c11a6e49e) |
| iOS | [映屿 iOS](https://www.pgyer.com/yingyu-ios-q) | [1.1.25](https://www.pgyer.com/app/build/a20fed577a3f1f19285c2b06d82629c6) |

本版补齐手机端更新发布通道，加入同名影片跨片源线路聚合、当前播放地址重试和最多三条备用线路恢复，优化缓冲、暂停续播及清晰度切换。Android 为 ARMv7、ARM64、x86_64 通用 APK，保持原包名和签名；iOS 为 Ad Hoc，仅供描述文件内已登记的 5 台设备安装。

Android 在 App 内解析蒲公英公开页、显示下载进度、校验大小和 SHA-256，并交给系统安装器。TV 保留 TCL 内置多屏互动安装交接。iOS 的“前往安装”打开蒲公英安装页，由系统完成安装，不在 App 内调用 Android 安装流程。

## 更新频道

[updates.json](https://api.github.com/repos/arvin-manager/yingyu/contents/updates.json?ref=main) 通过以下独立条目提供当前版本：

| `pgyerChannels` 键 | 应用身份 |
| --- | --- |
| `android-mobile` | Android `com.kankan.kankan` |
| `android-tv` | Android `com.kankan.kankan.tv` |
| `ios-mobile` | iOS `com.kankan.kankan` |

客户端按平台和手机/TV 类型选择条目，只有更高构建号才提示更新。首页每 6 小时自动检查一次，设置中可手动检查。未配置的通道不报告其他平台更新。

旧版 `channels` 保留原 GitHub APK 条目，避免不支持蒲公英解析的客户端把 HTML 当作安装包。非常旧的版本需先从蒲公英手动覆盖安装一次；不能只改清单就让旧二进制获得解析能力。历史 [GitHub Releases](https://github.com/arvin-manager/yingyu/releases) 继续保留。

## 后续发布

1. 提高版本号与构建号，保留包名和现有签名。不同 APK 字节不能复用同一构建号。
2. Flutter 工程使用 `tool/build_android.sh mobile` / `tool/build_android.sh tv`，正式入口 `lib/main.dart`，不拆分 ABI；iOS 使用相同正式入口归档并按现有个人团队 Ad Hoc 配置导出。
3. 上传对应蒲公英应用并发布，记录具体 `/app/build/<buildKey>` 页面，不能用会随上传漂移的短链替代清单中的固定版本页。
4. Android 发布前，使用 Flutter 工程的 `tool/pgyer_public_download_probe.dart` 从公开固定页面完整下载，确认与本地签名 APK 的大小、SHA-256 一致，再运行 `scripts/publish_pgyer.py`。脚本重新检查包名、签名及通用架构，保留旧频道，拒绝降低或替换既有构建号。
5. iOS 导出后验证 IPA 代码签名、Bundle ID、构建号、个人团队和 Ad Hoc 描述文件设备；公开固定页面确认平台与版本后，用 IPA 的实际大小和 SHA-256 更新 `pgyerChannels.ios-mobile`。
6. 提交清单并推送，回读 GitHub API 确认三个通道与产物一致。只提交公开元数据，不提交 APK/IPA、私钥、UDID 名单、账号 API Key 或 OSS 临时签名地址。

公开页面仅解析必要字段，完成正常 token 校验和官方跳转，不执行远程 JavaScript，不绕过验证码、登录、密码或付费限制。页面变化或额外授权会停止下载并提示错误。Android 客户端保留完整性检查，兼容性由系统安装器判断；发布脚本的包名和签名校验继续保留。

历史 GitHub 附件仍由 `scripts/update_feed.py` 校验后使用已确认的 `https://gh-proxy.com/` 下载代理。此规则不替代当前蒲公英分发。

## 发布脚本检查

```sh
python3 -m unittest discover -s scripts -p 'test_*.py'
```

本仓库仅存放公开分发配置、说明和自动化，Flutter 源码仍在本地维护。

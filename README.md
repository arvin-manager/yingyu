# 映屿 · 更新与安装包

映屿 Android 手机 / Android TV 的公开更新分发仓库。使用 GitHub Releases 存放安装包，使用静态版本文件提供 App 内更新检查，无需服务器或蒲公英 API Key。

- [下载已发布的版本](https://github.com/arvin-manager/yingyu/releases)
- [App 使用的更新文件](https://raw.githubusercontent.com/arvin-manager/yingyu/main/updates.json)
- TV 的蒲公英分发页：https://www.pgyer.com/yingyutv

初始化时更新文件的频道为空，表示暂未在 GitHub 发布安装包，不会给 App 推送虚构更新。当前旧安装包没有自动更新功能，**首次接入版需要手动安装一次**。

## 发布新版本

1. 在 Flutter 工程提高版本与构建号，比如 `1.1.10+5012`。保持现有包名和签名证书。
2. 显式构建需要的版本：`tool/build_android.sh tv` 或 `tool/build_android.sh mobile`。使用通用 release APK，含 ARMv7、ARM64、x86_64；正式入口为 `lib/main.dart`。
3. 打开本仓库 **Releases → Draft a new release**。填写新 tag（例如 `v1.1.10-tv`）及更新说明，**先上传 APK，再点 Publish release**。一个 Release 可以同时包含手机和 TV 包，但每个类型只能有一个 APK。
4. GitHub Actions 的 `Publish app update feed` 会读取实际 APK 的包名、versionName、versionCode、大小、SHA-256，校验签名和通用架构，然后自动提交 `updates.json`。
5. Actions 成功后 App 可读取新版本；GitHub CDN 通常可能缓存数分钟。App 每 6 小时自动检查一次，设置中可手动检查。

APK 通过 Release 的附件上传，不能提交到 Git 源码目录。无需配置个人 Token 或上传签名私钥；Actions 使用仓库自带的短期 `GITHUB_TOKEN`。

如果先发布后才上传 APK，或需要重新同步，打开 **Actions → Publish app update feed → Run workflow**，输入已发布的 tag。不要把“重新跑任务”当成提高构建号：修改了 APK 必须增加 versionCode。草稿和预发布版本不会进入稳定更新频道。

## 频道与覆盖安装

| 频道 | 包名 | 用途 |
| --- | --- | --- |
| `android-tv` | `com.kankan.kankan.tv` | 电视遥控器版本 |
| `android-mobile` | `com.kankan.kankan` | Android 手机版本 |
| `ios-mobile` | 暂未配置 | iOS 需要有效 Apple 签名及对应安装页 |

发布 TV 不会改变手机频道，反之亦然。下载地址使用用户确认可用的 `https://gh-proxy.com/` 代理并固定到具体 Release，例如 `https://gh-proxy.com/https://github.com/arvin-manager/yingyu/releases/download/v1.1.13-tv/yingyu-tv-1.1.13-universal.apk`；后续发布另一频道也不会下载到错误安装包。版本检查仍使用 GitHub API，发布脚本校验官方附件身份后生成代理下载链接。App 下载后检查 SHA-256，再由 Android 检查包名、版本及证书，最后由用户在系统安装器确认安装。不会静默安装。

`signing-certificates.json` 只保存已分发 APK 的**公开证书指纹**，不含私钥或 keystore。自动化拒绝签名不一致的包，防止发布后无法覆盖安装。若以后改用正式证书，应先安排已有安装版本的迁移，不能只修改这里的指纹。

GitHub 域名在部分网络上可能无法访问；检查失败不会阻止 App 使用，可稍后重试或通过蒲公英手动安装。

## 检查发布脚本

```sh
python3 -m unittest discover -s scripts -p 'test_*.py'
```

该仓库只存放分发配置、说明及自动化。Flutter 工程仍在本地维护。

# OpenClaw + 飞书命令整理清单

来源：`/Users/allenchoi/Documents/openclaw安装指南.md`

## 1. OpenClaw 基础

```bash
npm i -g openclaw
sudo npm i -g openclaw
openclaw --version
openclaw version
openclaw help
openclaw configure
openclaw dashboard
openclaw doctor
openclaw health
```

## 2. Gateway 控制

```bash
openclaw gateway install
openclaw gateway start
openclaw gateway run
openclaw gateway run --allow-unconfigured
openclaw gateway status
openclaw gateway stop
openclaw gateway restart
```

## 3. 配置命令（含飞书）

```bash
openclaw config
openclaw config get channels.feishu
openclaw config set channels.feishu.streaming true
openclaw config set channels.feishu.streaming false
openclaw config set channels.feishu.footer.elapsed true
openclaw config set channels.feishu.footer.status true
openclaw config set channels.feishu.requireMention true --json
openclaw config set channels.feishu.requireMention false --json
openclaw config set channels.feishu.requireMention open --json
openclaw config set channels.feishu.groups.oc_xxxxxxxx.requireMention true --json
```

## 4. 飞书插件引导命令

```bash
npm config set registry https://registry.npmjs.org
curl -o /tmp/feishu-openclaw-plugin-onboard-cli.tgz https://sf3-cn.feishucdn.com/obj/open-platform-opendoc/195a94cb3d9a45d862d417313ff62c9c_gfW8JbxtTd.tgz
npm install /tmp/feishu-openclaw-plugin-onboard-cli.tgz -g
sudo npm install /tmp/feishu-openclaw-plugin-onboard-cli.tgz -g
rm /tmp/feishu-openclaw-plugin-onboard-cli.tgz

feishu-plugin-onboard install
feishu-plugin-onboard doctor
feishu-plugin-onboard doctor --fix
```

## 5. 配对与飞书斜杠命令

```bash
openclaw pairing approve feishu <PAIRING_CODE> --notify
/feishu start
/feishu auth
/feishu doctor
```

## 6. 运行态查询

```bash
openclaw plugins list
openclaw status
openclaw instances list
openclaw alerts list --unread
openclaw tasks list --running
openclaw logs tail --lines 100
```

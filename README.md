# ondemand-dex
[read the docs](https://osc.github.io/ood-documentation/latest/authentication/dex.html)

## Session Support

This repo builds optional session support based on the following original commit:

https://github.com/juliantaylor/dex/commit/b3fc3e6c2295c0af166803bdde0977ed170d1d40

During new version updates , use the following process to get the that patch into the newest version. The following is for v2.45.1

```shell
# Current branch would be git checkout -b session-support-v2.44.0
git checkout -b session-support-v2.45.1

git remote update

git rebase v2.45.1

git log
```

Capture the new session commit SHA and use for RPM and Deb package patches.

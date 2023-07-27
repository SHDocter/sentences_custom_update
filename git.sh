#!/bin/bash
cp -r /root/sentences/sentences/*.json /root/hitokoto/

function git_command {
git add .
git commit -am "update"
git push
}

cd /root/hitokoto
git_command
echo "已执行推送"

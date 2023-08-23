#!/bin/bash

for file in seq_1_frame_*.bin; do
    # 提取数字部分
    num=$(echo "$file" | grep -o '[0-9]\+\.bin' | cut -d. -f1)
    
    # 用printf格式化数字，使其有3位，不足的补0
    newname=$(printf "%03d.bin" "$num")
    
    # 重命名文件
    mv "$file" "$newname"
done
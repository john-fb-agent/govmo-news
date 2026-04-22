#!/usr/bin/env python3
"""Test basic inference"""
import subprocess

prompt = "Classify this news to one category: 金融財政、經濟產業、科技創新、文化體育、交通運輸、教育發展、人才發展、國家安全、社會服務、政府管治\n\nNews: 金管局赴深圳舉辦澳門投資基金業務推介活動，吸引約95名來自兩地政府部門、行業協會代表出席。"

print("Testing basic inference...")
result = subprocess.run([
    '/home/js/.npm-global/bin/openclaw', 'infer', 'model', 'run',
    '--prompt', prompt,
    '--model', 'qwen/qwen3.5-plus'
], capture_output=True, text=True, timeout=60)

print(f"Return code: {result.returncode}")
print(f"Output: {result.stdout[:500] if result.stdout else '(empty)'}")
if result.stderr:
    print(f"Error: {result.stderr[:500]}")

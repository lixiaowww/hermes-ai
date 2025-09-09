#!/usr/bin/env python3
"""
测试前端界面变化
"""
import requests
import re
from bs4 import BeautifulSoup

def test_frontend_changes():
    """测试前端界面的变化"""
    base_url = "http://localhost:3002"
    
    print("🔍 测试前端界面变化...")
    
    try:
        # 测试主页面
        print("\n1. 测试主页面...")
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找导航链接
            nav_links = soup.find_all('a', class_=re.compile(r'text-gray-700'))
            print(f"   找到 {len(nav_links)} 个导航链接:")
            
            for link in nav_links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                print(f"   - {text}: {href}")
            
            # 检查是否包含Prototype链接
            prototype_links = [link for link in nav_links if 'prototype' in link.get('href', '').lower()]
            if prototype_links:
                print("   ✅ 找到Prototype链接!")
            else:
                print("   ❌ 未找到Prototype链接")
                
        else:
            print(f"   ❌ 主页面返回状态码: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ 主页面测试失败: {e}")
    
    try:
        # 测试原型页面
        print("\n2. 测试原型页面...")
        response = requests.get(f"{base_url}/prototype", timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找页面标题
            title = soup.find('h1')
            if title:
                print(f"   页面标题: {title.get_text(strip=True)}")
            
            # 查找表单元素
            textarea = soup.find('textarea')
            if textarea:
                print("   ✅ 找到需求输入框")
            
            select = soup.find('select')
            if select:
                print("   ✅ 找到应用类型选择器")
            
            button = soup.find('button')
            if button:
                print(f"   ✅ 找到按钮: {button.get_text(strip=True)}")
                
        else:
            print(f"   ❌ 原型页面返回状态码: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ 原型页面测试失败: {e}")
    
    try:
        # 测试后端API
        print("\n3. 测试后端API...")
        response = requests.get("http://localhost:8000/external-agents/agents", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 后端API正常，找到 {len(data.get('agents', []))} 个Agent")
        else:
            print(f"   ❌ 后端API返回状态码: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ 后端API测试失败: {e}")

if __name__ == "__main__":
    test_frontend_changes()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
公司数据初始化脚本
创建companies表并插入默认公司数据
"""

import json
from app import app, db
from models import Company

def init_companies():
    """初始化公司数据"""
    
    with app.app_context():
        # 创建表
        db.create_all()
        
        # 检查是否已有数据
        if Company.query.count() > 0:
            print("公司数据已存在，跳过初始化")
            return
        
        # 默认公司数据
        default_companies = [
            {
                'name': '阿里巴巴',
                'company_type': 'big_tech',
                'difficulty': 4.2,
                'description': '中国最大的电商和云计算公司，注重技术深度和业务理解。',
                'tech_stack': json.dumps(['Vue', 'React', '算法', '系统设计']),
                'question_count': 12,
                'pass_rate': 65,
                'is_default': True
            },
            {
                'name': '腾讯',
                'company_type': 'big_tech',
                'difficulty': 3.8,
                'description': '中国领先的互联网公司，以社交和游戏业务著称。',
                'tech_stack': json.dumps(['React', 'JavaScript', '微信生态']),
                'question_count': 8,
                'pass_rate': 72,
                'is_default': True
            },
            {
                'name': '字节跳动',
                'company_type': 'big_tech',
                'difficulty': 4.5,
                'description': '全球化的互联网公司，以抖音、今日头条等产品闻名。',
                'tech_stack': json.dumps(['算法', '性能优化', '编程实现']),
                'question_count': 15,
                'pass_rate': 58,
                'is_default': True
            },
            {
                'name': '百度',
                'company_type': 'big_tech',
                'difficulty': 3.5,
                'description': '中国领先的搜索引擎和AI公司。',
                'tech_stack': json.dumps(['前端基础', '框架应用', '工程化思维']),
                'question_count': 6,
                'pass_rate': 78,
                'is_default': True
            },
            {
                'name': '美团',
                'company_type': 'big_tech',
                'difficulty': 3.9,
                'description': '中国领先的生活服务电商平台。',
                'tech_stack': json.dumps(['业务理解', '技术实现', '解决方案']),
                'question_count': 7,
                'pass_rate': 69,
                'is_default': True
            },
            {
                'name': '京东',
                'company_type': 'big_tech',
                'difficulty': 3.6,
                'description': '中国领先的电商和零售基础设施服务商。',
                'tech_stack': json.dumps(['技术深度', '编程能力']),
                'question_count': 5,
                'pass_rate': 75,
                'is_default': True
            },
            {
                'name': '网易',
                'company_type': 'big_tech',
                'difficulty': 3.7,
                'description': '中国领先的互联网技术公司，以游戏、邮箱、音乐等产品著称。',
                'tech_stack': json.dumps(['游戏开发', '前端技术']),
                'question_count': 4,
                'pass_rate': 73,
                'is_default': True
            }
        ]
        
        # 插入数据
        for company_data in default_companies:
            company = Company(**company_data)
            db.session.add(company)
        
        try:
            db.session.commit()
            print(f"成功初始化 {len(default_companies)} 个默认公司")
            
            # 显示插入的公司
            companies = Company.query.all()
            print("\n已插入的公司:")
            for company in companies:
                print(f"- {company.name} (ID: {company.id}, 类型: {company.company_type})")
                
        except Exception as e:
            db.session.rollback()
            print(f"初始化失败: {e}")

if __name__ == '__main__':
    print("开始初始化公司数据...")
    init_companies()
    print("初始化完成!")

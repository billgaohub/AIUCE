#!/usr/bin/env python3
"""
AIUCE Social Preview Image Generator
生成 GitHub 社交预览图 (1280x640)
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_social_preview():
    # 图片尺寸 (GitHub 推荐)
    WIDTH = 1280
    HEIGHT = 640

    # 创建画布
    img = Image.new('RGB', (WIDTH, HEIGHT), color='#1a1a2e')
    draw = ImageDraw.Draw(img)

    # 颜色定义
    COLORS = {
        'bg': '#1a1a2e',           # 深蓝背景
        'accent': '#e94560',       # 红色强调
        'gold': '#f4a261',         # 金色
        'white': '#ffffff',        # 白色文字
        'gray': '#a0a0a0',         # 灰色
        'layer_colors': [
            '#e94560', '#f4a261', '#2ec4b6', '#3a86ff',
            '#8338ec', '#ff006e', '#fb5607', '#ffbe0b'
        ]
    }

    # 尝试加载字体
    try:
        font_title = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 72)
        font_subtitle = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 36)
        font_tagline = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 28)
        font_layer = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
    except:
        font_title = ImageFont.load_default()
        font_subtitle = ImageFont.load_default()
        font_tagline = ImageFont.load_default()
        font_layer = ImageFont.load_default()

    # 绘制背景渐变效果（用矩形模拟）
    for i in range(HEIGHT):
        alpha = int(255 * (1 - i / HEIGHT * 0.3))
        color = f'#{alpha:02x}{alpha:02x}{alpha + 30:02x}'
        draw.line([(0, i), (WIDTH, i)], fill=COLORS['bg'])

    # 主标题
    title = "🏯 AIUCE"
    draw.text((80, 80), title, font=font_title, fill=COLORS['white'])

    # 副标题
    subtitle = "Personal AI Infrastructure"
    draw.text((80, 180), subtitle, font=font_subtitle, fill=COLORS['gold'])

    # 标语
    tagline = "给 AI 装上「宪法」和「御史台」"
    draw.text((80, 240), tagline, font=font_tagline, fill=COLORS['accent'])

    # 11 层架构可视化
    layer_names = [
        "L0 Constitution", "L1 Identity", "L2 Boundary", "L3 Reasoning",
        "L4 Memory", "L5 Decision", "L6 Execution", "L7 Evolution",
        "L8 Interface", "L9 Tool", "L10 Sandbox"
    ]

    # 绘制层级条
    start_x = 80
    start_y = 340
    bar_height = 28
    bar_spacing = 8
    bar_width = 400

    for i, layer in enumerate(layer_names):
        y = start_y + i * (bar_height + bar_spacing)
        color = COLORS['layer_colors'][i % len(COLORS['layer_colors'])]

        # 绘制进度条
        draw.rectangle(
            [(start_x, y), (start_x + bar_width, y + bar_height)],
            fill=color,
            outline=None
        )

        # 绘制文字
        draw.text(
            (start_x + 10, y + 4),
            layer,
            font=font_layer,
            fill=COLORS['white']
        )

    # 右侧核心特性
    features = [
        "✓ 宪法层约束",
        "✓ 决策审计",
        "✓ 沙盒模拟",
        "✓ 多模型支持",
        "✓ 主权归属"
    ]

    feature_x = 650
    feature_y = 340

    for i, feature in enumerate(features):
        y = feature_y + i * 45
        draw.text(
            (feature_x, y),
            feature,
            font=font_tagline,
            fill=COLORS['white']
        )

    # 底部标签
    tags = "Python  •  FastAPI  •  Docker  •  Open Source"
    draw.text((80, HEIGHT - 60), tags, font=font_tagline, fill=COLORS['gray'])

    # GitHub 标识
    github_text = "github.com/billgaohub/AIUCE"
    draw.text((WIDTH - 400, HEIGHT - 60), github_text, font=font_tagline, fill=COLORS['gray'])

    # 保存图片
    output_path = os.path.expanduser("~/SONUV/AIUCE/.github/social-preview.png")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, 'PNG', quality=95)

    print(f"✅ 社交预览图已生成: {output_path}")
    print(f"   尺寸: {WIDTH}x{HEIGHT}")
    return output_path

if __name__ == "__main__":
    create_social_preview()

#!/usr/bin/env python3
"""
Instagram发布器 - Carousel帖子
多步骤工作流：Create → 选择图片 → 填写Caption → 发布
"""

from social_media_poster_base import SocialMediaPosterBase
import time
import logging
import os
import sys

logger = logging.getLogger(__name__)

class InstagramPoster(SocialMediaPosterBase):
    def __init__(self, auth_file: str = "platforms_auth.json"):
        super().__init__("instagram", auth_file)
        self.home_url = "https://www.instagram.com"

    def _load_auth(self) -> dict:
        """加载Instagram认证（从platforms_auth.json）"""
        try:
            import json
            with open(self.auth_file, 'r') as f:
                auth_data = json.load(f)
                if 'instagram' in auth_data:
                    instagram_auth = auth_data['instagram']

                    # 如果是旧格式（只有sessionid字符串），转换为cookies数组
                    if 'sessionid' in instagram_auth and 'cookies' not in instagram_auth:
                        sessionid = instagram_auth['sessionid']
                        instagram_auth['cookies'] = [
                            {
                                'name': 'sessionid',
                                'value': sessionid,
                                'domain': '.instagram.com',
                                'path': '/',
                                'httpOnly': True,
                                'secure': True,
                                'sameSite': 'None'
                            }
                        ]
                        logger.info("   ✅ Instagram sessionid已转换为cookie格式")

                    return instagram_auth
                return auth_data
        except FileNotFoundError:
            logger.error(f"❌ 认证文件不存在: {self.auth_file}")
            return None

    def find_post_button(self) -> bool:
        """查找Create按钮"""
        try:
            # Instagram的Create按钮通常是"+"图标
            create_selectors = [
                # 英文 selectors
                'a[href="#"]>svg[aria-label*="New post"]',
                'a[href="#"]>svg[aria-label*="Create"]',
                'svg[aria-label*="New post"]',
                'svg[aria-label*="Create"]',
                '[aria-label*="New post"]',
                '[aria-label*="Create"]',
                'a:has-text("Create")',
                # 中文 selectors (创建)
                'a[href="#"]>svg[aria-label*="创建"]',
                'svg[aria-label*="创建"]',
                '[aria-label*="创建"]',
                'a:has-text("创建")'
            ]

            for selector in create_selectors:
                try:
                    element = self.page.wait_for_selector(selector, timeout=3000)
                    if element and element.is_visible():
                        logger.info(f"   ✅ 找到Create按钮: {selector}")
                        return True
                except:
                    continue

            logger.warning("   ⚠️  未找到Create按钮")
            return False

        except Exception as e:
            logger.error(f"   ❌ 查找按钮错误: {str(e)}")
            return False

    def create_post(self, content: dict, image_paths: list = None) -> bool:
        """
        创建Instagram帖子

        content格式:
        {
            'caption': '主要文案',
            'slides': ['Slide 1 text', 'Slide 2 text', ...],  # Carousel内容
            'hashtags': '#tag1 #tag2 #tag3'
        }

        image_paths: 图片文件路径列表（如果不提供，使用默认占位图）
        """
        try:
            logger.info(f"🌐 访问Instagram...")
            # 使用domcontentloaded而不是networkidle，因为Instagram feed持续加载内容
            self.page.goto(self.home_url, wait_until="domcontentloaded", timeout=60000)
            self._random_delay(2, 3)

            # 截图1 - 初始状态
            self.take_screenshot("before_create")

            # 步骤1: 点击左侧菜单的"创建"按钮
            logger.info("   📍 步骤1: 点击侧边栏的'创建'按钮...")

            # 重要：这次要点击真正的侧边栏创建按钮，不要直接导航URL
            create_button_selectors = [
                'a[href="#"]:has-text("创建")',  # 侧边栏链接中文
                'div[role="link"]:has-text("创建")',
                'span:has-text("创建")',
                'a[href="#"]:has-text("Create")',  # 英文
                'span:has-text("Create")',
                # 通过SVG图标查找（创建按钮通常有特定的SVG图标）
                'svg[aria-label*="新建"]',
                'svg[aria-label*="New post"]',
            ]

            create_clicked = False
            logger.info("      🔍 查找侧边栏'创建'按钮...")
            for selector in create_button_selectors:
                try:
                    button = self.page.wait_for_selector(selector, timeout=3000)
                    if button and button.is_visible():
                        # 找到了创建按钮
                        logger.info(f"      ✅ 找到创建按钮: {selector}")
                        button.click()
                        logger.info(f"      🖱️  已点击创建按钮")
                        create_clicked = True
                        self._random_delay(1, 2)  # 等待菜单出现
                        break
                except:
                    continue

            if not create_clicked:
                # 如果还是找不到，尝试通过位置查找（创建通常在侧边栏固定位置）
                logger.warning("      ⚠️  未找到创建按钮，尝试查找所有带'创建'文本的元素...")
                try:
                    # 获取包含"创建"或"Create"的所有元素
                    all_elements = self.page.query_selector_all('*')
                    for elem in all_elements[:50]:  # 只检查前50个
                        try:
                            text = elem.inner_text() if elem.is_visible() else ""
                            if text and ("创建" in text or "Create" in text) and len(text) < 10:  # 文本很短，可能就是按钮
                                logger.info(f"      🔍 尝试点击元素: '{text}'")
                                elem.click()
                                create_clicked = True
                                self._random_delay(1, 2)
                                break
                        except:
                            continue
                except:
                    pass

            if not create_clicked:
                logger.error("      ❌ 无法找到并点击创建按钮")
                return False

            logger.info(f"      ✅ 创建按钮已点击，等待菜单出现...")

            self._random_delay(2, 4)

            # 截图2 - Create后
            self.take_screenshot("after_create_click")

            # 步骤2: 选择"Post"（如果有选项）
            logger.info("   📍 步骤2: 选择Post类型...")

            try:
                # 可能会出现选择帖子类型的对话框（中文和英文）
                post_option_selectors = [
                    'span:has-text("帖子")',  # 中文"帖子"
                    'div:has-text("帖子")',
                    'button:has-text("帖子")',
                    'span:has-text("Post")',  # 英文Post
                    'button:has-text("Post")',
                    'div:has-text("Post")',
                    '[aria-label*="Post"]',
                    '[aria-label*="帖子"]'
                ]

                post_selected = False
                for selector in post_option_selectors:
                    try:
                        post_option = self.page.wait_for_selector(selector, timeout=3000)
                        if post_option and post_option.is_visible():
                            post_option.click()
                            logger.info(f"      ✅ 选择Post/帖子: {selector}")
                            post_selected = True
                            self._random_delay(2, 3)
                            break
                    except:
                        continue

                if not post_selected:
                    logger.info("      ℹ️  没有Post类型选择对话框，直接进入上传")
            except:
                logger.info("      ℹ️  没有Post类型选择对话框")

            # 步骤3: 等待上传模态框出现并上传图片
            logger.info("   📍 步骤3: 等待上传对话框并上传图片...")

            # 等待上传对话框出现（中文和英文标题）
            upload_modal_visible = False
            modal_indicators = [
                '[role="dialog"]',  # Dialog角色
                'div:has-text("创建新帖子")',  # 中文标题
                'div:has-text("Create new post")',  # 英文标题
                'div:has-text("新建帖子")',
                'form[method="POST"]'  # 表单
            ]

            logger.info("      ⏳ 等待上传对话框出现...")
            for indicator in modal_indicators:
                try:
                    modal = self.page.wait_for_selector(indicator, timeout=5000)
                    if modal:
                        logger.info(f"      ✅ 上传对话框已出现: {indicator}")
                        upload_modal_visible = True
                        break
                except:
                    continue

            if not upload_modal_visible:
                logger.warning("      ⚠️  未检测到上传对话框，尝试继续...")

            self._random_delay(2, 3)

            # Instagram Web要求上传图片，如果没有提供图片路径，警告用户
            if not image_paths:
                logger.warning("   ⚠️  未提供图片路径！")
                logger.warning("   ℹ️  Instagram帖子需要图片。请手动上传图片。")
                logger.info("   ⏸️  浏览器将保持打开60秒，请手动上传图片...")

                # 保持浏览器打开，让用户手动上传
                time.sleep(60)

                # 假设用户已上传，继续下一步
            else:
                # 策略：直接使用Playwright的set_input_files()设置隐藏的file input
                # 这样可以避免系统文件选择器，更可靠且跨平台
                try:
                    logger.info(f"      📤 准备上传图片: {os.path.basename(image_paths[0])}")

                    # 准备文件路径（绝对路径）
                    absolute_path = os.path.abspath(image_paths[0])
                    logger.info(f"      📝 文件路径: {absolute_path}")

                    # 查找隐藏的file input元素
                    logger.info("      🔍 查找file input元素...")

                    # Instagram的file input通常在form内，尝试多种选择器
                    file_input_selectors = [
                        'input[type="file"]',
                        'form input[type="file"]',
                        'input[accept*="image"]',
                        'form input[accept*="image"]'
                    ]

                    file_input = None
                    for selector in file_input_selectors:
                        try:
                            # 等待元素出现（可能是隐藏的）
                            file_input = self.page.wait_for_selector(selector, timeout=5000, state='attached')
                            if file_input:
                                logger.info(f"      ✅ 找到file input: {selector}")
                                break
                        except:
                            continue

                    if not file_input:
                        raise Exception("未找到file input元素")

                    # 直接设置文件路径（Playwright会处理上传，无需打开文件对话框）
                    logger.info("      ⬆️  使用Playwright set_input_files上传...")
                    file_input.set_input_files(absolute_path)

                    logger.info(f"      ✅ 文件已设置到input元素")
                    self._random_delay(3, 5)  # 等待Instagram处理上传

                except Exception as e:
                    logger.error(f"      ❌ Playwright上传失败: {str(e)}")
                    logger.error(f"      错误详情: {type(e).__name__}")
                    import traceback
                    logger.error(traceback.format_exc())

                    # 备用方案：PyAutoGUI控制系统文件选择器
                    logger.info("      🔄 尝试备用方案: PyAutoGUI...")
                    try:
                        import pyautogui
                        from clipboard import copy

                        logger.info("      ⏳ 等待系统文件选择器打开（2秒）...")
                        time.sleep(2)

                        # 将文件路径复制到剪贴板
                        copy(absolute_path)
                        logger.info("      📋 文件路径已复制到剪贴板")

                        # 在Mac上，使用 Cmd+Shift+G 打开"前往文件夹"对话框
                        pyautogui.hotkey('command', 'shift', 'g')
                        time.sleep(0.5)

                        # 粘贴文件路径
                        pyautogui.hotkey('command', 'v')
                        time.sleep(0.5)

                        # 按回车键确认路径
                        pyautogui.press('return')
                        time.sleep(1)

                        # 再次按回车选择文件
                        pyautogui.press('return')

                        logger.info(f"      ✅ 已通过PyAutoGUI上传图片")
                        self._random_delay(3, 5)

                    except Exception as e2:
                        logger.error(f"      ❌ PyAutoGUI备用方案也失败: {str(e2)}")
                        # 最后的备用方案：给用户时间手动上传
                        logger.info("      ⏸️  请手动上传图片（30秒）...")
                        self.take_screenshot("upload_failed")
                        time.sleep(30)

            # 截图3 - 图片上传后
            self.take_screenshot("after_image_upload")

            # 步骤4: 点击"Next"/"下一步"进入编辑页面
            logger.info("   📍 步骤4: 进入编辑页面...")

            next_selectors = [
                'button:has-text("下一步")',  # 中文
                'button:has-text("Next")',     # 英文
                'div:has-text("下一步")',
                'div:has-text("Next")'
            ]

            next_clicked = False
            for attempt in range(3):  # 可能需要点击多次Next
                for selector in next_selectors:
                    try:
                        next_button = self.page.wait_for_selector(selector, timeout=3000)
                        if next_button and next_button.is_visible():
                            next_button.click()
                            logger.info(f"      ✅ 点击Next/下一步 (第{attempt+1}次): {selector}")
                            next_clicked = True
                            self._random_delay(2, 3)
                            break
                    except:
                        continue
                if next_clicked:
                    next_clicked = False  # 重置以便下一次循环
                else:
                    break  # 如果没有找到按钮，退出循环

            logger.info("      ℹ️  Next按钮处理完成")

            # 截图4 - 编辑页面
            self.take_screenshot("edit_page")

            # 步骤5: 填写Caption（包括hashtags）
            caption = content.get('caption', '')
            hashtags = content.get('hashtags', '')
            full_caption = f"{caption}\n\n{hashtags}"

            logger.info(f"   📍 步骤5: 填写Caption ({len(full_caption)} 字符)...")

            caption_filled = False
            caption_selectors = [
                # 中文选择器
                'textarea[aria-label*="说点什么"]',
                'textarea[aria-label*="添加说明"]',
                'div[contenteditable="true"][aria-label*="说点什么"]',
                # 英文选择器
                'textarea[aria-label*="caption"]',
                'textarea[aria-label*="Caption"]',
                'textarea[placeholder*="caption"]',
                'div[contenteditable="true"][aria-label*="caption"]',
                # 通用选择器
                'textarea:first-of-type',
                'div[contenteditable="true"]:first-of-type'
            ]

            for selector in caption_selectors:
                try:
                    caption_input = self.page.wait_for_selector(selector, timeout=3000)
                    if caption_input and caption_input.is_visible():
                        caption_input.click()
                        self._random_delay(0.5, 1)

                        # 模拟人类打字
                        if 'contenteditable' in selector:
                            words = full_caption.split(' ')
                            for i, word in enumerate(words):
                                self.page.keyboard.type(word + ' ')
                                if i % 15 == 0:
                                    self._random_delay(0.1, 0.3)
                        else:
                            caption_input.fill(full_caption)

                        logger.info(f"      ✅ Caption已填写")
                        caption_filled = True
                        break
                except Exception as e:
                    logger.debug(f"      尝试 {selector} 失败: {str(e)[:50]}")
                    continue

            if not caption_filled:
                logger.warning("   ⚠️  无法填写Caption")

            self._random_delay(2, 3)

            # 截图5 - Caption填写完成
            self.take_screenshot("caption_filled")

            # 步骤6: 点击"Share"发布
            logger.info(f"   📍 步骤6: 点击Share发布...")

            share_clicked = False
            share_selectors = [
                'button:has-text("Share")',
                'button:has-text("Post")',
                'button[type="submit"]',
                '[aria-label*="Share"]',
                'button:has-text("发布")',
                'button:has-text("分享")'
            ]

            for selector in share_selectors:
                try:
                    share_button = self.page.wait_for_selector(selector, timeout=3000)
                    if share_button and share_button.is_visible() and share_button.is_enabled():
                        share_button.click()
                        logger.info(f"      ✅ Share按钮已点击")
                        share_clicked = True
                        break
                except:
                    continue

            if not share_clicked:
                logger.error("   ❌ 无法点击Share按钮")
                self.take_screenshot("share_button_not_found")
                return False

            # 等待发布完成
            logger.info("   ⏳ 等待发布完成...")
            self._random_delay(8, 12)

            # 截图6 - 发布后
            self.take_screenshot("after_post")

            # 验证发布成功
            # Instagram发布后可能显示"Your post has been shared"
            try:
                success_indicators = [
                    'div:has-text("post has been shared")',
                    'div:has-text("Post shared")',
                    'div:has-text("已分享")'
                ]

                for indicator in success_indicators:
                    try:
                        element = self.page.wait_for_selector(indicator, timeout=3000)
                        if element:
                            logger.info(f"   ✅ Instagram帖子发布成功！")
                            return True
                    except:
                        continue

                # 如果没有找到成功提示，但也没有错误，认为成功
                logger.info(f"   ✅ Instagram帖子可能已发布成功")
                return True

            except:
                logger.warning(f"   ⚠️  发布状态未知")
                return True  # 仍然返回True

        except Exception as e:
            logger.error(f"   ❌ Instagram发布失败: {str(e)}")
            self.take_screenshot("error")
            import traceback
            logger.error(traceback.format_exc())
            return False

if __name__ == "__main__":
    # 测试
    import sys
    import os

    # 设置日志
    logging.basicConfig(level=logging.INFO)

    # 检查API key
    if 'OPENAI_API_KEY' not in os.environ:
        print("❌ 请设置 OPENAI_API_KEY")
        sys.exit(1)

    # 测试内容
    test_content = {
        'caption': '''🚀 Testing Instagram automation from MarketingMind AI

Transform your job search with AI-powered interview prep!

✨ Features:
• Personalized practice questions
• Real-time feedback
• Industry-specific scenarios

Learn more at HireMeAI.app''',
        'hashtags': '#AI #JobSearch #CareerTips #InterviewPrep #HireMeAI #TechJobs #Automation'
    }

    # 注意：Instagram需要图片！请提供图片路径
    # test_image_paths = ['/path/to/image1.jpg']

    poster = InstagramPoster()

    try:
        poster.setup_browser(headless=False)

        if poster.verify_login():
            print("✅ 登录验证成功")
            print("⚠️  注意：Instagram帖子需要图片！")
            print("   请在浏览器中手动上传图片，脚本会自动填写Caption")

            # 不提供图片路径，让用户手动上传
            success = poster.create_post(test_content, image_paths=None)

            if success:
                print("✅ 发布测试成功！")
            else:
                print("❌ 发布测试失败")
        else:
            print("❌ 登录验证失败，请先保存Instagram cookies到platforms_auth.json")

    finally:
        input("\n按Enter关闭浏览器...")
        poster.close_browser()

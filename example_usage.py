#!/usr/bin/env python3
"""
Instagram API 快速开始示例

这个脚本演示如何使用 Instagram API SDK
"""

from instagram_sdk import InstagramAPI, InstagramAPIError
import sys


def print_section(title):
    """打印章节标题"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


def main():
    # 初始化 API（自动添加延迟防止速率限制）
    api = InstagramAPI(
        auto_delay=True,
        min_delay=3,
        max_delay=8
    )

    # 检查服务状态
    print_section("检查 API 服务状态")

    if not api.is_available():
        print("❌ API 服务未运行")
        print("\n请先启动以下服务：")
        print("\n终端 1:")
        print("  cd /Users/l.u.c/my-app/uniapi/backend")
        print("  uvicorn main:app --reload --port 8000")
        print("\n终端 2:")
        print("  cd /Users/l.u.c/my-app/uniapi/backend")
        print("  python3 platforms/instagram/instagram_bridge_server.py")
        sys.exit(1)

    print("✅ API 服务正常运行")

    # ==================== 示例 1: 获取用户资料 ====================
    print_section("示例 1: 获取用户资料")

    username = "instagram"  # 可以替换为任何用户名
    print(f"正在获取用户 @{username} 的资料...")

    try:
        user = api.get_user(username)

        print("\n用户信息：")
        print(f"  👤 用户名: {user['username']}")
        print(f"  🔗 主页: {user['profile_url']}")
        print(f"  📝 简介: {user.get('bio', 'N/A')}")
        print(f"  👥 粉丝: {user.get('followers', 'N/A')}")

    except InstagramAPIError as e:
        print(f"❌ 错误: {e}")

    # ==================== 示例 2: 点赞帖子 ====================
    print_section("示例 2: 点赞帖子")

    # 注意：需要替换为真实的帖子 URL
    post_url = input("\n请输入要点赞的帖子 URL (按Enter跳过): ").strip()

    if post_url:
        print(f"\n正在点赞帖子: {post_url}")

        try:
            result = api.like_post(post_url)

            if result['success']:
                print("✅ 点赞成功！")
            else:
                print(f"❌ 点赞失败: {result.get('message')}")

        except InstagramAPIError as e:
            print(f"❌ 错误: {e}")
    else:
        print("⏭️  跳过点赞示例")

    # ==================== 示例 3: 关注用户 ====================
    print_section("示例 3: 关注用户")

    target_user = input("\n请输入要关注的用户名 (按Enter跳过): ").strip()

    if target_user:
        print(f"\n正在关注 @{target_user}...")

        try:
            result = api.follow(target_user)

            if result['success']:
                print(f"✅ 已关注 @{target_user}")
            else:
                print(f"❌ 关注失败: {result.get('message')}")

        except InstagramAPIError as e:
            print(f"❌ 错误: {e}")
    else:
        print("⏭️  跳过关注示例")

    # ==================== 示例 4: 评论帖子 ====================
    print_section("示例 4: 评论帖子")

    comment_url = input("\n请输入要评论的帖子 URL (按Enter跳过): ").strip()

    if comment_url:
        comment_text = input("请输入评论内容: ").strip()

        if comment_text:
            print(f"\n正在发表评论...")

            try:
                result = api.comment(comment_url, comment_text)

                if result['success']:
                    print(f"✅ 评论成功: \"{comment_text}\"")
                else:
                    print(f"❌ 评论失败: {result.get('message')}")

            except InstagramAPIError as e:
                print(f"❌ 错误: {e}")
    else:
        print("⏭️  跳过评论示例")

    # ==================== 示例 5: 获取用户帖子 ====================
    print_section("示例 5: 获取用户帖子列表")

    posts_user = input("\n请输入用户名 (按Enter使用默认: instagram): ").strip() or "instagram"

    print(f"\n正在获取 @{posts_user} 的帖子...")

    try:
        posts = api.get_user_posts(posts_user, limit=10)

        print(f"\n找到 {len(posts)} 个帖子：")
        for i, post in enumerate(posts[:5], 1):
            print(f"  {i}. {post['url']}")

        if len(posts) > 5:
            print(f"  ... 还有 {len(posts) - 5} 个帖子")

    except InstagramAPIError as e:
        print(f"❌ 错误: {e}")

    # ==================== 示例 6: 搜索标签 ====================
    print_section("示例 6: 搜索标签")

    tag = input("\n请输入要搜索的标签 (按Enter使用默认: travel): ").strip() or "travel"

    print(f"\n正在搜索标签 #{tag}...")

    try:
        results = api.search_by_tag(tag, limit=10)

        print(f"\n找到 {len(results)} 个帖子：")
        for i, post in enumerate(results[:5], 1):
            print(f"  {i}. {post['url']}")

        if len(results) > 5:
            print(f"  ... 还有 {len(results) - 5} 个帖子")

    except InstagramAPIError as e:
        print(f"❌ 错误: {e}")

    # ==================== 示例 7: 发送私信 ====================
    print_section("示例 7: 发送私信")

    dm_user = input("\n请输入要发送私信的用户名 (按Enter跳过): ").strip()

    if dm_user:
        dm_message = input("请输入私信内容: ").strip()

        if dm_message:
            print(f"\n正在发送私信给 @{dm_user}...")

            try:
                result = api.send_dm(dm_user, dm_message)

                if result['success']:
                    print(f"✅ 私信已发送给 @{dm_user}")
                else:
                    print(f"❌ 发送失败: {result.get('message')}")

            except InstagramAPIError as e:
                print(f"❌ 错误: {e}")
    else:
        print("⏭️  跳过私信示例")

    # ==================== 示例 8: 批量点赞 ====================
    print_section("示例 8: 批量点赞（高级）")

    print("\n批量点赞可以一次性点赞多个帖子")
    batch_test = input("是否测试批量点赞? (yes/no): ").strip().lower()

    if batch_test == 'yes':
        print("\n请输入帖子 URL，每行一个，输入空行结束：")
        urls = []
        while True:
            url = input().strip()
            if not url:
                break
            urls.append(url)

        if urls:
            print(f"\n正在批量点赞 {len(urls)} 个帖子...")
            print("（操作间隔 5 秒）")

            try:
                results = api.batch_like(urls, delay=5)

                success_count = sum(1 for r in results if r.get('success'))
                print(f"\n✅ 成功: {success_count}/{len(results)}")
                print(f"❌ 失败: {len(results) - success_count}/{len(results)}")

            except InstagramAPIError as e:
                print(f"❌ 错误: {e}")
    else:
        print("⏭️  跳过批量点赞示例")

    # 完成
    print_section("示例演示完成")
    print("\n✅ 所有示例运行完毕！")
    print("\n📚 更多信息请查看：")
    print("  • 用户指南: INSTAGRAM_API_USER_GUIDE.md")
    print("  • 测试指南: INSTAGRAM_TESTING_GUIDE.md")
    print("  • SDK 文档: instagram_sdk.py")
    print("\n感谢使用 Instagram API! 🎉\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

#!/bin/bash
# Twitter Login Script - One-time setup for authentication

set -e

echo "============================================================"
echo "🔐 Twitter Authentication Setup"
echo "============================================================"
echo ""
echo "This script will open a browser where you can login to Twitter."
echo "Your login session will be saved for future use."
echo ""
echo "⚠️  IMPORTANT:"
echo "  - Use a real Twitter account (not a test account)"
echo "  - Do NOT close the browser manually"
echo "  - Wait for the script to finish"
echo ""
read -p "Press Enter to continue..."
echo ""

# Activate virtual environment
cd backend
source venv/bin/activate

# Run the login script
python3 << 'EOF'
import asyncio
from playwright.async_api import async_playwright
import os
from pathlib import Path

async def twitter_login():
    """Interactive Twitter login with persistent browser context"""

    # Setup browser context directory
    context_dir = Path.home() / ".distroflow" / "twitter_browser"
    context_dir.mkdir(parents=True, exist_ok=True)

    print("🌐 Opening browser...")
    print("")

    async with async_playwright() as p:
        # Launch browser with GUI
        browser = await p.chromium.launch(headless=False)

        # Create persistent context to save cookies
        context = await browser.new_context(
            user_data_dir=str(context_dir),
            viewport={"width": 1280, "height": 800}
        )

        page = await context.new_page()

        print("✅ Browser opened")
        print("")
        print("📋 Instructions:")
        print("  1. Login to Twitter in the browser window")
        print("  2. Complete any 2FA/verification if prompted")
        print("  3. Wait until you see your Twitter homepage")
        print("  4. Come back here and press Enter")
        print("")

        # Open Twitter
        await page.goto("https://twitter.com/login")

        # Wait for user to login
        input("Press Enter after you've logged in to Twitter...")

        # Verify login by checking for home page
        try:
            await page.goto("https://twitter.com/home", timeout=10000)
            print("")
            print("🔍 Verifying login...")

            # Check if we're on the home page (logged in)
            if "home" in page.url.lower():
                print("✅ Login successful!")
                print(f"✅ Session saved to: {context_dir}")
            else:
                print("⚠️  Warning: Could not verify login. You may need to try again.")
        except Exception as e:
            print(f"⚠️  Warning: Verification failed: {e}")
            print("   Your session may still be saved. Try running the start script.")

        # Close browser
        await context.close()
        await browser.close()

        print("")
        print("✅ Setup complete!")
        print("")
        print("You can now use UniAPI to access Twitter without API keys.")

if __name__ == "__main__":
    asyncio.run(twitter_login())
EOF

cd ..

echo ""
echo "============================================================"
echo "🎉 Authentication Complete!"
echo "============================================================"
echo ""
echo "Next steps:"
echo "  1. Start UniAPI: ./start.sh"
echo "  2. Test API:     python3 backend/test_twitter_api.py"
echo ""

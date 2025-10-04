@echo off
echo Installing Python dependencies for chat...
pip install openai==1.3.0
pip install Pillow==10.1.0
pip install python-dotenv==1.0.0
echo.
echo Dependencies installed! Now enabling chat features...
echo.
echo Please edit server/core/settings.py and replace 'sk-your-openai-api-key-here' with your real OpenAI API key
echo Get your API key from: https://platform.openai.com/api-keys
echo.
pause

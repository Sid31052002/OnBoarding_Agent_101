# logger.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("F:/Freelance/Onboarding-Agent/backend/logs/onboarding_agent.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("onboarding-agent")

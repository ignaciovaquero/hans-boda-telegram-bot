import asyncio
import logging
import os
import sys
import telegram

ENV_PREFIX: str = "HANS_BODA"

logging.basicConfig(
    level=logging.DEBUG if os.getenv(f"{ENV_PREFIX}_DEBUG", False) else logging.INFO
)
logger = logging.getLogger(__name__)


TELEGRAM_TOKEN: str = os.getenv(f"{ENV_PREFIX}_TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID: str = os.getenv(f"{ENV_PREFIX}_TELEGRAM_CHAT_ID", "-950108034")

TRUE_STRING: str = "true"


def _check_python_version(version: tuple[int, int]) -> None:
    """Checks that the Python version used is greater or equal to `version`.

    Args:
        version (tuple[int, int]): The minimum Python version allowed.

    Raises:
        RuntimeError: Raised when the Python version is lower than `version`.
    """
    if sys.version_info < version:
        raise RuntimeError(
            f"Python version must be greater or equal to {version[0]}.{version[1]}"
        )


async def send_telegram(message: str) -> None:
    """Sends a telegram message.

    Args:
        message (str): The message to be sent.

    Raises:
        ValueError: Raised when there is no HANS_BODA_TELEGRAM_TOKEN
        environment variable specified.
    """
    if not TELEGRAM_TOKEN:
        raise ValueError("Telegram token can't be empty")
    bot: telegram.Bot = telegram.Bot(TELEGRAM_TOKEN)
    async with bot:
        logger.debug("sending message to chat %s", TELEGRAM_CHAT_ID)
        await bot.send_message(text=message, chat_id=int(TELEGRAM_CHAT_ID))


def lambda_handler(event, context):
    _check_python_version((3, 9))
    action_message: str = "Un invitado ha contestado."
    for record in event["Records"]:
        if record["eventName"] == "MODIFY":
            action_message = "Un invitado ha cambiado sus respuestas."
        name: str = record["dynamodb"]["Keys"]["Name"]
        last_name: str = record["dynamodb"]["Keys"]["LastName"]
        coming: bool = record["dynamodb"]["Keys"]["Coming"] == TRUE_STRING
        allergy: bool = record["dynamodb"]["Keys"]["Allergy"] == TRUE_STRING
        allergy_text: str = record["dynamodb"]["Keys"]["AllergyText"]
        bus: bool = record["dynamodb"]["Keys"]["Bus"] == TRUE_STRING
        bus_back: bool = record["dynamodb"]["Keys"]["BusBack"] == TRUE_STRING
        bus_time: int = int(record["dynamodb"]["Keys"]["BusTime"])
        message: str = f"""
        {action_message}

        Nombre: {name}
        Apellidos: {last_name}
        - El invitado indica que {"sí" if coming else "no"} vendrá a la boda.
        """

        if coming:
            message = f"""
            {message}
            - El invitado indica que{"" if allergy else " no"} tiene{" las siguientes" if allergy else ""} alergias{f": {allergy_text}" if allergy else "."}
            - El invitado indica que{"" if bus else " no"} cogerá el autobús a la ida.
            - El invitado indica que{"" if bus_back else " no"} cogerá el autobús de vuelta{f" a la{' 01:00' if not bus_time else 's 04:00'}" if bus_back else ""}.
            """
        logger.debug("sending telegram message for %s %s", name, last_name)
        send_telegram(message=message)

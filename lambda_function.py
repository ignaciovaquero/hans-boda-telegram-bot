import asyncio
import logging
import os
import sys
import telegram

ENV_PREFIX: str = "HANS_BODA"

logger = logging.getLogger()
logger.setLevel(
    level=logging.DEBUG if os.getenv(f"{ENV_PREFIX}_DEBUG", False) else logging.INFO
)


TELEGRAM_TOKEN: str = os.getenv(f"{ENV_PREFIX}_TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID: str = os.getenv(f"{ENV_PREFIX}_TELEGRAM_CHAT_ID", "-1001555706515")


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


async def main(event):
    tasks: list[asyncio.Task] = []

    action_message: str = "Un invitado ha contestado."
    for record in event["Records"]:
        if record["eventName"] == "REMOVE":
            logger.error("received invalid event 'REMOVE'")
            continue
        if record["eventName"] == "MODIFY":
            action_message = "Un invitado ha cambiado sus respuestas."
        name: str = record["dynamodb"]["NewImage"]["Name"]["S"].title()
        last_name: str = record["dynamodb"]["NewImage"]["LastName"]["S"].title()
        coming: bool = record["dynamodb"]["NewImage"]["Coming"]["BOOL"]
        allergy: bool = record["dynamodb"]["NewImage"]["Allergy"]["BOOL"]
        allergy_text: str = record["dynamodb"]["NewImage"]["AllergyText"][
            "S"
        ].capitalize()
        bus: bool = record["dynamodb"]["NewImage"]["Bus"]["BOOL"]
        bus_back: bool = record["dynamodb"]["NewImage"]["BusBack"]["BOOL"]
        bus_time: int = int(record["dynamodb"]["NewImage"]["BusTime"]["N"])
        bus_location: str = record["dynamodb"]["NewImage"]["BusLocation"]["S"]
        bus_back_location: str = record["dynamodb"]["NewImage"]["BusBackLocation"]["S"]
        logger.debug("Creating message for guest %s %s", name, last_name)
        message: str = (
            f"{action_message}\n\n"
            f"Nombre: {name}\n"
            f"Apellidos: {last_name}\n\n"
            f"- El invitado indica que {'sí' if coming else 'no'} vendrá a la boda.\n"
        )
        if coming:
            message = (
                f"{message}"
                f"- El invitado indica que{'' if allergy else ' no'} tiene{' las siguientes' if allergy else ''} alergias{f': {allergy_text}' if allergy else '.'}\n"
                f"- El invitado indica que{'' if bus else ' no'} cogerá el autobús a la ida{f' desde {bus_location}' if bus else ''}.\n"
                f"""- El invitado indica que{"" if bus_back else " no"} cogerá el autobús de vuelta{f" a la{' 01:30' if not bus_time else 's 04:30'}" if bus_back else ""}{f' desde {bus_back_location}' if bus_back else ''}.\n\n\n"""
            )
        tasks.append(asyncio.create_task(send_telegram(message=message)))

    await asyncio.gather(*tasks)


def lambda_handler(event, context):
    _check_python_version((3, 9))
    logger.debug("DynamoDB event received: %s", event)
    asyncio.run(main=main(event=event))

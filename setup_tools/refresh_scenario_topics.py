#!/usr/bin/env python3
"""
Refresh scenario topic ids in client_config.json for an existing forum.
"""

import asyncio
import json
from pathlib import Path
import sys

from pyrogram import Client, raw

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from analysis.scenario_classifier import SCENARIO_NAMES


CONFIG_PATH = Path("client_config.json")


async def refresh_scenario_topics():
    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        config = json.load(file)

    app = Client(
        "scenario_forum_setup_user",
        api_id=config["api_id"],
        api_hash=config["api_hash"],
        phone_number=config["phone_number"],
    )

    async with app:
        for forwarder in config.get("scenario_forwarders", []):
            forum_chat_id = forwarder["forum_chat_id"]
            forum_peer = await app.resolve_peer(forum_chat_id)
            input_channel = to_input_channel(forum_peer)
            topics = await fetch_scenario_topics(app, input_channel)

            missing_topics = [scenario for scenario in SCENARIO_NAMES if scenario not in topics]
            if missing_topics:
                print(f"⚠️  Fórum {forum_chat_id}: {len(missing_topics)} cenário(s) sem tópico:")
                for scenario in missing_topics:
                    print(f"   - {scenario}")

            forwarder["scenario_topics"] = topics
            print(f"✅ Fórum {forum_chat_id}: {len(topics)} tópico(s) sincronizados")

    with CONFIG_PATH.open("w", encoding="utf-8") as file:
        json.dump(config, file, indent=2, ensure_ascii=False)

    print("✅ client_config.json atualizado")


async def fetch_scenario_topics(app, input_channel):
    result = await app.invoke(
        raw.functions.channels.GetForumTopics(
            channel=input_channel,
            offset_date=0,
            offset_id=0,
            offset_topic=0,
            limit=100,
        )
    )

    scenario_topics = {}
    for topic in getattr(result, "topics", []):
        title = getattr(topic, "title", "")
        if title in SCENARIO_NAMES:
            scenario_topics[title] = {
                "message_thread_id": int(topic.id),
                "top_msg_id": int(getattr(topic, "top_message", None) or topic.id),
            }
    return scenario_topics


def to_input_channel(peer):
    if isinstance(peer, raw.types.InputPeerChannel):
        return raw.types.InputChannel(
            channel_id=peer.channel_id,
            access_hash=peer.access_hash,
        )
    if isinstance(peer, raw.types.InputChannel):
        return peer
    raise ValueError(f"Peer não é um canal/supergrupo: {type(peer).__name__}")


if __name__ == "__main__":
    asyncio.run(refresh_scenario_topics())

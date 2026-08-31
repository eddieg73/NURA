from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx

from .models import CoordinationNotification, HermesEvent


class NotionSinkError(RuntimeError):
    pass


class NotionCoordinationSink:
    def __init__(self, *, token: str, data_source_id: str, api_version: str, timeout_seconds: float = 10.0) -> None:
        self.data_source_id = data_source_id
        self.client = httpx.Client(
            base_url="https://api.notion.com/v1",
            timeout=timeout_seconds,
            headers={
                "Authorization": f"Bearer {token}",
                "Notion-Version": api_version,
                "Content-Type": "application/json",
                "User-Agent": "nura-hermes-event-bridge/1.0",
            },
        )

    def close(self) -> None:
        self.client.close()

    def publish(self, event: HermesEvent) -> str:
        notification = event.notification
        if notification is None:
            raise NotionSinkError("Event has no coordination notification")
        properties = self._properties(event, notification)
        if notification.target_page_id:
            response = self.client.patch(
                f"/pages/{notification.target_page_id}", json={"properties": properties}
            )
        else:
            response = self.client.post(
                "/pages",
                json={
                    "parent": {"type": "data_source_id", "data_source_id": self.data_source_id},
                    "properties": properties,
                },
            )
        if response.status_code >= 400:
            request_id = response.headers.get("x-request-id", "unknown")
            raise NotionSinkError(f"Notion API returned {response.status_code}; request_id={request_id}")
        payload = response.json()
        page_id = payload.get("id")
        if not page_id:
            raise NotionSinkError("Notion API response did not include a page ID")
        return str(page_id)

    @staticmethod
    def _properties(event: HermesEvent, notification: CoordinationNotification) -> dict[str, Any]:
        review_notes = (
            f"Hermes event {event.event_id} | {event.event_type} | source={event.source_service}. "
            f"{notification.summary}"
        )[:1900]
        properties: dict[str, Any] = {
            "Work Item": {"title": [{"type": "text", "text": {"content": notification.work_item}}]},
            "Lane": {"select": {"name": notification.lane}},
            "Owner": {"select": {"name": notification.owner}},
            "Priority": {"select": {"name": notification.priority}},
            "Review Notes": {"rich_text": [{"type": "text", "text": {"content": review_notes}}]},
            "Reviewer": {"select": {"name": notification.reviewer}},
            "Status": {"select": {"name": notification.status}},
            "Type": {"select": {"name": notification.work_type}},
            "Updated": {"date": {"start": datetime.now(timezone.utc).date().isoformat()}},
        }
        if notification.link:
            properties["Link"] = {"url": str(notification.link)}
        return properties

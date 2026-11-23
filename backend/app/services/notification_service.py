"""Compatibility wrapper for Notification Service."""

from backend.app.services.whatsapp_service import WhatsAppNotificationService, whatsapp_service

__all__ = ["WhatsAppNotificationService", "whatsapp_service"]

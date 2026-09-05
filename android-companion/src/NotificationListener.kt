package com.pulse.ai.companion

import android.service.notification.NotificationListenerService
import android.service.notification.StatusBarNotification
import android.util.Log
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

/**
 * Android NotificationListenerService for PULSE AI.
 * Captures user-authorized SMS and notification alerts (e.g. Bank SMS, Utility Bills, Recharge reminders)
 * and securely forwards normalized payloads to the PULSE AI backend `/api/v1/mobile/notifications` endpoint.
 */
class PulseNotificationListener : NotificationListenerService() {

    private val scope = CoroutineScope(Dispatchers.IO)
    private val apiClient = PulseApiClient()

    override fun onNotificationPosted(sbn: StatusBarNotification?) {
        super.onNotificationPosted(sbn)
        if (sbn == null) return

        val packageName = sbn.packageName
        val extras = sbn.notification.extras
        val title = extras.getString("android.title") ?: ""
        val text = extras.getCharSequence("android.text")?.toString() ?: ""

        // Filter supported notification sources (SMS, Banking apps, Utility services, Delivery alerts)
        if (isSupportedSource(packageName, title, text)) {
            Log.d("PulseNotification", "Captured notification from $packageName: $title")

            scope.launch {
                apiClient.sendNotification(
                    sourceApp = mapPackageToCategory(packageName),
                    title = title,
                    content = text
                )
            }
        }
    }

    private fun isSupportedSource(pkg: String, title: String, text: String): Boolean {
        val combined = "$pkg $title $text".lowercase()
        return combined.contains("sms") || 
               combined.contains("bill") || 
               combined.contains("due") || 
               combined.contains("recharge") || 
               combined.contains("bank") || 
               combined.contains("delivery")
    }

    private fun mapPackageToCategory(pkg: String): String {
        return when {
            pkg.contains("messaging") || pkg.contains("sms") -> "SMS"
            pkg.contains("bank") -> "Bank Alert"
            else -> "App Notification"
        }
    }
}
